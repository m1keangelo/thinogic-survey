#!/usr/bin/env python3
# Thinogic Survey Studio — server v4.2.0 (production hardened)
import os, re, json, time, secrets, base64, shutil, urllib.request, hashlib
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from urllib.parse import urlparse

STUDIO_VERSION = "4.2.0"
CLIENT_VERSION = "4.2.0"  # Bump both; report warns if mismatched
PORT  = int(os.environ.get("PORT", "8000"))
KEY   = os.environ.get("KIMI_API_KEY", "")
AUTHU = os.environ.get("AUTH_USER", "jerry")
AUTHP = os.environ.get("AUTH_PASS", "changeme-now")
# Multi-user: AUTH_USERS="user1:pass1,user2:pass2" or empty (fall back to AUTH_USER:AUTH_PASS)
MULTI = os.environ.get("AUTH_USERS", "")
HERE  = os.path.dirname(os.path.abspath(__file__))
DATA  = os.environ.get("DATA_DIR", HERE)
PUB   = os.path.join(DATA, "public")
SURV  = os.path.join(DATA, "surveys")
SESSF = os.path.join(DATA, "sessions.json")
CURF  = os.path.join(DATA, "current_survey.txt")
IMGSF = os.path.join(DATA, "images")  # Persistent image cache
LEGACY= os.path.join(DATA, "studio_state.json")
for d in (PUB, SURV, IMGSF): os.makedirs(d, exist_ok=True)

# Validate auth setup
CREDS = {}
if MULTI:
    for pair in MULTI.split(","):
        if ":" in pair:
            u, p = pair.split(":", 1)
            CREDS[u.strip()] = p.strip()
if not CREDS:
    CREDS[AUTHU] = AUTHP  # Fallback

SESSIONS = {}  # {token: {user, expires}}
if os.path.exists(SESSF):
    try:
        old = json.load(open(SESSF))
        if isinstance(old, dict): SESSIONS = old
        elif isinstance(old, list):
            # Migrate from old token-only format to new {token: {...}} format
            for t in old: SESSIONS[t] = {"user": "unknown", "expires": time.time() + 2592000}
    except Exception: pass

def save_sessions():
    try: json.dump(SESSIONS, open(SESSF, "w"))
    except Exception: pass

def sweep_sessions():
    """Remove expired sessions (30+ day old)."""
    now = time.time()
    expired = [t for t, v in SESSIONS.items() if v.get("expires", 0) < now]
    for t in expired: SESSIONS.pop(t, None)
    if expired: save_sessions()

def load_index():
    f = os.path.join(SURV, "index.json")
    if os.path.exists(f):
        try: return json.load(open(f))
        except Exception: pass
    return {}

def save_index(ix):
    try: json.dump(ix, open(os.path.join(SURV, "index.json"), "w"))
    except Exception: pass

def safe_name(n): return re.sub(r"[^A-Za-z0-9._-]", "_", n or "file")[:80]
def state_path(cid): return os.path.join(SURV, safe_name(cid) + ".json")
def img_path(sid, iid): return os.path.join(IMGSF, safe_name(sid), safe_name(iid) + ".b64")

def cur_id():
    if os.path.exists(CURF):
        c = open(CURF).read().strip()
        if c and os.path.exists(state_path(c)): return c
    return "default"

def touch(ix, cid, data):
    try:
        s = (data or {}).get("S", {})
        ix[cid] = {"name": (s.get("meta") or {}).get("name") or ix.get(cid, {}).get("name") or cid,
                   "updated": time.time(), "photos": len(s.get("photos", []))}
    except Exception: pass

# Migrate legacy single state -> default survey
if os.path.exists(LEGACY) and not os.path.exists(state_path("default")):
    shutil.copy(LEGACY, state_path("default"))
_ix = load_index()
if "default" not in _ix and os.path.exists(state_path("default")):
    touch(_ix, "default", json.load(open(state_path("default")))); save_index(_ix)

def session_of(h):
    """Extract session token from HttpOnly SameSite=Lax cookie."""
    c = h.get("Cookie", "")
    if not c: return None
    try:
        m = SimpleCookie(); m.load(c)
        t = m.get("tl_sess")
        if not t: return None
        val = t.value
        # Refresh from disk (multi-container safe)
        if os.path.exists(SESSF):
            try:
                SESSIONS.update(json.load(open(SESSF)))
            except Exception: pass
        return val if val in SESSIONS else None
    except Exception: pass
    return None

def check_csrf(h, method):
    """CSRF hardening: Origin/Referer check on state-changing POSTs."""
    if method not in ("POST", "PUT", "DELETE"): return True
    origin = h.get("Origin", "")
    referer = h.get("Referer", "")
    host = h.get("Host", "")
    if not origin and not referer: return False  # No origin info = reject
    if origin:
        try: origin_host = urlparse(origin).netloc
        except: return False
        if origin_host != host: return False
    if referer:
        try: ref_host = urlparse(referer).netloc
        except: return False
        if ref_host != host: return False
    return True

def route_get(self):
    if self.path in ("/", "/index.html", "/studio"):
        return self._file(os.path.join(HERE, "studio_hosted.html"), "text/html; charset=utf-8")
    if self.path.startswith("/public/"):
        p = self.path[len("/public/"):].split("?")[0]
        ct = "application/pdf" if p.lower().endswith(".pdf") else "text/html; charset=utf-8"
        return self._file(os.path.join(PUB, safe_name(p)), ct)
    if self.path == "/api/health":
        # Coolify health check endpoint (no auth required for infra)
        return self._json(200, {"ok": True, "version": STUDIO_VERSION})
    if self.path == "/api/version":
        return self._json(200, {"studio": STUDIO_VERSION, "client": CLIENT_VERSION})
    if self.path == "/api/state":
        if not session_of(self.headers): return self._json(401, {"error": "login required"})
        p = state_path(cur_id())
        if os.path.exists(p): return self._json(200, json.load(open(p)))
        return self._json(200, {"S": {"meta": {"name": "Default"}}})
    if self.path == "/api/surveys":
        if not session_of(self.headers): return self._json(401, {"error": "login required"})
        ix = load_index()
        lst = [{"id": k, "name": v.get("name", k), "updated": v.get("updated", 0), "photos": v.get("photos", 0)} for k, v in ix.items()]
        lst.sort(key=lambda x: x["updated"], reverse=True)
        return self._json(200, {"current": cur_id(), "list": lst})
    if self.path.startswith("/proxy/"):
        if not session_of(self.headers): return self._json(401, {"error": "login required"})
        if not KEY: return self._json(503, {"error": "KIMI_API_KEY not configured"})
        url = "https://" + self.path[len("/proxy/"):]
        headers = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                self.send_response(200); self.send_header("Content-Type", "application/json")
                self.end_headers(); self.wfile.write(r.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code); self.end_headers(); self.wfile.write(e.read())
        except Exception as e: self._json(502, {"error": str(e)})
        return
    self.send_response(404); self.end_headers()

def route_post(self, body):
    if self.path == "/api/login":
        try: d = json.loads(body.decode() or "{}")
        except Exception: return self._json(400, {"error": "bad json"})
        u, p = d.get("u"), d.get("p")
        if u in CREDS and CREDS[u] == p:
            t = secrets.token_hex(16)
            SESSIONS[t] = {"user": u, "expires": time.time() + 2592000}
            save_sessions()
            return self._json(200, {"ok": True},
                [("Set-Cookie", "tl_sess=%s; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000" % t)])
        return self._json(401, {"error": "bad credentials"})
    if self.path == "/api/logout":
        t = session_of(self.headers)
        if t: SESSIONS.pop(t, None); save_sessions()
        return self._json(200, {"ok": True}, [("Set-Cookie", "tl_sess=; Path=/; HttpOnly; Max-Age=0")])
    
    # All other POST endpoints require session
    if not session_of(self.headers):
        return self._json(401, {"error": "login required"})
    
    # CSRF hardening
    if not check_csrf(self.headers, "POST"):
        return self._json(403, {"error": "csrf"})
    
    if self.path == "/api/state":
        try: data = json.loads(body.decode() or "{}")
        except Exception: return self._json(400, {"error": "bad json"})
        cid = cur_id(); p = state_path(cid); tmp = p + ".tmp"
        open(tmp, "wb").write(body); os.replace(tmp, p)
        ix = load_index(); touch(ix, cid, data); save_index(ix)
        return self._json(200, {"ok": True, "saved": time.time(), "survey": cid})
    
    if self.path == "/api/survey/new":
        try: d = json.loads(body.decode() or "{}")
        except Exception: return self._json(400, {"error": "bad json"})
        name = (d.get("name") or "Untitled").strip()[:80] or "Untitled"
        cid = safe_name(name)[:40] + "-" + str(int(time.time()))[-6:]
        st = {"S": {"meta": {"name": name, "created": time.time()}}}
        json.dump(st, open(state_path(cid), "w"))
        open(CURF, "w").write(cid)
        ix = load_index(); touch(ix, cid, st); save_index(ix)
        os.makedirs(os.path.join(IMGSF, cid), exist_ok=True)
        return self._json(200, {"ok": True, "id": cid, **st})
    
    if self.path == "/api/survey/switch":
        try: d = json.loads(body.decode() or "{}")
        except Exception: return self._json(400, {"error": "bad json"})
        cid = safe_name(d.get("id", ""))
        if not cid or not os.path.exists(state_path(cid)):
            return self._json(404, {"error": "survey not found"})
        open(CURF, "w").write(cid)
        return self._json(200, json.load(open(state_path(cid))))
    
    if self.path == "/api/upload":
        """Persist original base64 image for server-side caching."""
        try:
            d = json.loads(body.decode() or "{}")
            sid, iid = safe_name(d.get("survey", cur_id())), safe_name(d.get("id", ""))
            content = d.get("content", "")  # base64
            if not iid or not content: return self._json(400, {"error": "missing id or content"})
            idir = os.path.join(IMGSF, sid)
            os.makedirs(idir, exist_ok=True)
            ipath = img_path(sid, iid)
            open(ipath, "w").write(content)
            return self._json(200, {"ok": True, "url": "/api/image/" + sid + "/" + iid})
        except Exception as e: return self._json(400, {"error": str(e)})
    
    if self.path == "/api/publish":
        try:
            d = json.loads(body.decode() or "{}")
            name = safe_name(d.get("name", "survey.html"))
            if "." not in name: name += ".html"
            raw = base64.b64decode(d["content"]) if d.get("b64") else d.get("content", "").encode()
            if len(raw) > 60 * 1024 * 1024: return self._json(413, {"error": "file too large"})
            open(os.path.join(PUB, name), "wb").write(raw)
            return self._json(200, {"ok": True, "url": "/public/" + name})
        except Exception as e: return self._json(400, {"error": str(e)})
    
    if self.path.startswith("/proxy/"):
        if not KEY: return self._json(503, {"error": "KIMI_API_KEY not configured"})
        url = "https://" + self.path[len("/proxy/"):]
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json", "Authorization": "Bearer " + KEY})
        try:
            with urllib.request.urlopen(req, timeout=150) as r:
                self.send_response(200); self.send_header("Content-Type", "application/json")
                self.end_headers(); self.wfile.write(r.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code); self.end_headers(); self.wfile.write(e.read())
        except Exception as e: self._json(502, {"error": str(e)})
        return
    
    self.send_response(404); self.end_headers()

class H(BaseHTTPRequestHandler):
    def _json(self, code, obj, extra=None):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        for k, v in (extra or []): self.send_header(k, v)
        self.end_headers(); self.wfile.write(b)
    
    def _file(self, path, ctype):
        if not os.path.exists(path):
            self.send_response(404); self.end_headers(); return
        b = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
        if ctype.startswith("text/html"): self.send_header("Cache-Control", "no-cache")
        self.end_headers(); self.wfile.write(b)
    
    def do_GET(self):
        route_get(self)
    
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        route_post(self, self.rfile.read(min(n, 70 * 1024 * 1024)))
    
    def log_message(self, *a): pass

os.chdir(HERE)
print("Thinogic hosted studio v4.2.0 on port", PORT)
print("Auth users:", ", ".join(CREDS.keys()))
# Sweep old sessions on startup
sweep_sessions()
ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
