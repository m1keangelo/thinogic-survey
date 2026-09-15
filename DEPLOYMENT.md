# Thinogic Survey Studio v4.2.0 — Deployment & Operations Guide

## Overview
Structured cabling assessment tool for Dumbarton Oaks RFP DOIT-2026-001. Python 3 stdlib-only server + vanilla JS SPA. Deployable to Coolify on Hostinger VPS or any Docker runtime.

**Current Version:** v4.2.0  
**Built for:** Dumbarton Oaks (Harvard), 9 buildings, RFP-compliant HTML/PDF/CSV exports  
**Status:** Production-hardened (18 known bugs fixed + forensic hardening)

---

## Quick Start (Coolify on Hostinger VPS)

### 1. Prerequisites
- Hostinger VPS (8 vCPU, 32GB RAM recommended; Coolify handles this)
- Kimi API key (https://platform.moonshot.cn/api-keys)
- Strong auth password (not "changeme-now")
- GitHub repo connected to Coolify (optional, for auto-deploy)

### 2. Create Service in Coolify UI
1. **Coolify Dashboard** → New Service → Docker Compose
2. **Paste this:**
   ```yaml
   services:
     thinogic:
       image: ghcr.io/yourusername/thinogic-studio:latest
       container_name: thinogic-studio
       ports:
         - "3000:8000"  # Traefik handles external routing; no host 8000 mapping
       environment:
         PORT: "8000"
         DATA_DIR: "/data"
         KIMI_API_KEY: "${KIMI_API_KEY}"
         AUTH_USER: "${AUTH_USER}"
         AUTH_PASS: "${AUTH_PASS}"
       volumes:
         - thinogic-data:/data  # CRITICAL: persistent
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   
   volumes:
     thinogic-data:
       driver: local
   ```

3. **Set Environment Variables** (under "Environment" tab):
   - **Production Set:**
     - `KIMI_API_KEY`: sk-xxx... (actual key)
     - `AUTH_USER`: jerry
     - `AUTH_PASS`: [strong-password]
     - `PORT`: 8000
     - `DATA_DIR`: /data
   
   - **Preview Set (separate):** Optional test environment with different credentials

4. **Configure Domain** (under "Domains" tab):
   - Add: `survey.thinklogic.global` (or your domain)
   - Traefik auto-enables HTTPS

5. **Deploy** → Coolify builds Docker image, deploys, and starts rolling updates

### 3. Verify Deployment
```bash
# SSH into VPS
ssh root@your-vps-ip

# Check container running
docker ps | grep thinogic

# Check volume mounted
docker exec thinogic-studio ls /data/surveys

# Test health endpoint
curl http://localhost:3000/api/health
# Expected: {"ok": true, "version": "4.2.0"}

# Check logs
docker logs -f thinogic-studio
```

### 4. First Login
1. Navigate to `https://survey.thinklogic.global`
2. Username: `jerry`
3. Password: [whatever you set in AUTH_PASS]
4. Click "Refresh Balance" to validate Kimi API connection

---

## Bug Fixes in v4.2.0

### Critical Issues Addressed

| Bug | Root Cause | Fix | Test |
|-----|-----------|-----|------|
| **Login loops** | HTTP Basic + Authorization header collision | Cookie-session auth (HttpOnly SameSite=Lax) + custom X-API-Key proxy header | POST /api/login → tl_sess cookie → validate every request from disk |
| **Server hang** | Single-threaded HTTP server blocked everything | ThreadingHTTPServer + 150s proxy timeout | Concurrent requests work; Kimi API timeouts handled gracefully |
| **Stale pages post-deploy** | No cache headers | Cache-Control: no-cache on HTML responses | Ctrl+Shift+R forces reload; server sends no-cache |
| **API 404 (model not on account)** | Hardcoded model name assumption | GET /v1/models; default fallback to kimi-k2.6 | Check /api/version response |
| **API 400 "invalid temp"** | Account enforces temperature=1 | Always send temperature=1 in all Kimi calls | Verify server/client always use temp=1 |
| **Reasoning models output** | Output in reasoning_content, not content | Read content OR reasoning_content; parseAIJSON handles both | Chat with kimi-k3 returns valid JSON |
| **ZIP parsing fails** | Naive local-header parser breaks on data-descriptor ZIPs | Central-directory parser (handles both flavors) | Drop ZIP with photos → all images found |
| **Port bind collision** | Host mapping collided with Coolify's 8000 | No host port mappings; Traefik routes internally | Service uses port 3000 → 8000 internally |
| **Data wiped every deploy** | No persistent volume | /data is Docker named volume (survives restarts) | Redeploy service → surveys/ still there |
| **Login loop #2** | Multiple containers + memory-only sessions | Sessions validated from shared disk; exactly one running container | Redeploy uses rolling-update; old container kills gracefully |
| **HEIC photos fail in Chrome** | Chrome can't decode HEIC | Detect browser; show warning; accept Safari or pre-convert | Upload HEIC in Safari → works; Chrome → shows banner |
| **Rate limits at 8 concurrent** | No retry backoff | callWithRetry: 5 attempts, exponential backoff + jitter, 429/5xx only | Burst 10 photos → callWithRetry retries rate-limited ones |
| **Cost overruns** | No balance checking or guardrails | GET /v1/users/me/balance; pre-flight cost estimate; hard-stop if balance < est | Balance banner shows $XX.XX; dialog warns before Pass 1 |
| **Version mismatch** | Static version text lied | Real version system: STUDIO_VERSION + CLIENT_VERSION in /api/version | Mismatch → red banner: "Reload to sync" |

---

## Forensic Hardening (v4.2.0)

### Implemented
✅ **#1 HEIC Support (CRITICAL)**
- Browser detection: Safari native HEIC support
- Chrome: Warning banner + suggestion to pre-convert
- Server-side conversion: Not implemented (breaks stdlib-only, acceptable per spec)
- **Acceptance:** Upload HEIC in Safari → Pass 1 succeeds on all photos

✅ **#3 Thumbnail Persistence** (fixed in v3+)
- Client caches in localStorage; server validates from disk on reload

✅ **#4 Health Check**
- GET /api/health endpoint → Coolify uses for rolling updates
- Stale container cleanup now works reliably

✅ **#6 CSRF Hardening**
- Origin/Referer checks on all POST requests
- Reject if no origin info or host mismatch
- SameSite=Lax + HttpOnly cookies prevent CSRF

✅ **#5 Multi-User Auth**
- AUTH_USERS env var: "user1:pass1,user2:pass2"
- Each user has separate session token (auth_sessions.json)
- Fallback to AUTH_USER/AUTH_PASS if AUTH_USERS empty

✅ **#7 Cost Guardrails**
- Pre-flight estimate: photo_count * (0.01 + 0.02 + 0.01) per pass
- Balance check: hard-stop if estimate > balance
- Live balance banner with refresh button

✅ **#14 Automated Test Battery**
- 14-server tests (auth, save/load, surveys CRUD, publish, session isolation, restart)
- 7-client tests (HEIC + ZIP, Pass 1 0-failed, cluster, public link)
- Run on every GitHub push (CI/CD recommended)

### Partially Implemented / Deferred
- **#2 Merge Direction (forensic):** Per-survey files mitigate; full merge safety still open (low priority)
- **#8 Folder→Building Mapping Template:** UI not yet built; recommend user-naming convention (zip by building name)
- **#9 Scanned PDF Support:** Fallback message shows "PDFs: best-effort text extraction, scans not fully supported"
- **#15 Pixel-Perfect PDF:** Would need server-side HTML→PDF (breaks stdlib-only goal; client-side print works)

---

## Environment Variable Checklist

**Before Deploying to Production:**

- [ ] **KIMI_API_KEY** set to actual key (get from https://platform.moonshot.cn)
- [ ] **AUTH_PASS** changed from "changeme-now" to strong password (min 12 chars)
- [ ] **AUTH_USER** customized if desired (default: jerry)
- [ ] **PORT** is 8000 (internal); external routing via Traefik
- [ ] **DATA_DIR** is /data (mounted persistent volume)
- [ ] Production and Preview environments separated (different creds in Coolify)
- [ ] Health check endpoint verified: `curl http://localhost:8000/api/health`
- [ ] Volume persisted: `docker exec <container> ls /data/surveys` shows survey files
- [ ] TLS/HTTPS enabled (required for SameSite=Lax cookies)
- [ ] GitHub webhook configured (if auto-deploy needed)
- [ ] Kimi key rotation scheduled (every 90 days)

---

## Troubleshooting

### "Login Required" Loop
**Symptom:** Always redirects to login, valid credentials fail.  
**Fix:**
1. Check Auth_PASS not "changeme-now" (real password set)
2. Verify TLS/HTTPS enabled (Traefik configured)
3. Check sessions.json readable: `docker exec thinogic-studio cat /data/sessions.json`
4. Restart container: `docker restart thinogic-studio`

### "Version Mismatch" Banner
**Symptom:** Red banner says "Studio v4.2.0 vs Client v4.1.4".  
**Fix:**
1. Server and client versions must match (both 4.2.0)
2. Hard-reload browser: Ctrl+Shift+R (not Ctrl+R)
3. Redeploy service (new image has correct client version)

### HEIC Photos Fail in Chrome
**Symptom:** Pass 1 fails on all .HEIC images, Chrome only.  
**Expected Behavior:** Warning banner suggests Safari or pre-conversion.  
**Fix:** Open in Safari or pre-convert photos to JPEG before upload.

### "Balance Low" / Cost Estimate Too High
**Symptom:** Balance banner shows $0.50 but trying to analyze 100 photos (est. $3.00).  
**Fix:**
1. Reload page to refresh balance
2. Add Kimi credits at https://platform.moonshot.cn
3. Reduce photo count per pass (e.g., 30 photos per survey instead of 100)

### Data Lost After Redeploy
**Symptom:** Surveys disappeared after Coolify rolling update.  
**Root Cause:** Volume not persisted.  
**Fix:**
1. Check volume mount: `docker inspect thinogic-studio | grep -A 5 "Mounts"`
2. Verify Coolify service config includes volume: `thinogic-data:/data`
3. Restore backup if available (always backup /data before upgrades)

### "Too Many Requests" (429) / Rate Limit Errors
**Symptom:** Kimi API returns 429; photos fail to analyze.  
**Root Cause:** 8 concurrent request limit at account level.  
**Fix:**
1. Server implements callWithRetry (5 attempts, exponential backoff)
2. Should auto-retry; if persistent, reduce concurrent photo uploads
3. Contact Kimi support to request higher rate limit

### Coolify Deployment Stalls / Old Container Doesn't Kill
**Symptom:** Rolling update takes >5min; two containers running; new one can't bind port.  
**Root Cause:** No health check endpoint; Coolify can't detect old container readiness.  
**Fix:**
1. Verify /api/health responds: `curl http://localhost:8000/api/health`
2. Restart Coolify (or manually kill old container: `docker stop <old-id>`)
3. Redeploy

---

## Local Development (No Coolify)

### Run Server Locally
```bash
# Set env vars
export KIMI_API_KEY="sk-xxx..."
export AUTH_USER=jerry
export AUTH_PASS=devpass
export DATA_DIR=./data
export PORT=8000

# Create data dir
mkdir -p data/surveys data/images data/public

# Run server
python3 hosted_server.py
# → "Thinogic hosted studio v4.2.0 on port 8000"
```

### Access UI
Open `http://localhost:8000` in browser.

### Test Health Endpoint
```bash
curl http://localhost:8000/api/health
# {"ok": true, "version": "4.2.0"}
```

### Test Balance Check
```bash
curl -H "Cookie: tl_sess=FAKE" http://localhost:8000/api/state
# 401: {"error": "login required"} (expected; no valid session)
```

---

## Acceptance Tests (v4.2.0)

### Server Battery (14 tests)
Run after every deployment:
```bash
# Example (pytest or curl-based)
pytest tests/server_battery.py -v

# Or manual:
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"u":"jerry","p":"devpass"}' | jq .  # Should return ok: true + Set-Cookie

curl -X POST http://localhost:8000/api/logout \
  -H "Cookie: tl_sess=..." \
  -H "Content-Type: application/json" | jq .  # Should return ok: true
```

### Client Battery (7 steps)
1. **Ingest:** Drop 5 images (3 JPG, 1 PNG, 1 HEIC) + 1 .txt file + 1 .zip
2. **Pass 1:** Click "Analyze All" → All 5 photos analyzed, 0 failed (HEIC in Safari)
3. **Disk Check:** localStorage + /data/surveys/<id>.json both have photo data
4. **Cluster:** Pass 2 groups by timestamps/labels (UI TBD)
5. **Lock:** Click "Lock" → Step 4 enabled
6. **Incognito:** Open public link in new incognito window → renders without login
7. **Survey Switch:** Create new survey → switch between surveys, isolation verified

---

## Version History (Production Path)

- **v3.0:** Initial hosted system (login, threading, no-cache, zip parser, docs)
- **v4.0.0:** Multi-survey database (`surveys/<id>.json`), named dropdown
- **v4.1.0:** Real version display (`STUDIO_VERSION + CLIENT_VERSION`)
- **v4.1.2:** Shared-disk sessions (multi-container safe)
- **v4.1.3:** Constants corrected
- **v4.1.4:** Failures ≠ done, re-analyze button, re-register handles, honest counts
- **v4.2.0:** HEIC detection, health endpoint, balance proxy, cost guardrails, rate-limit retry, CSRF hardening, multi-user auth

---

## Support & Issues

### Kimi API Documentation
- https://platform.moonshot.cn/docs
- Models: kimi-k2.6 (default), kimi-k3 (reasoning)
- Vision support: ✓ JPEG, PNG, HEIC, GIF; ✗ scanned PDFs (best-effort text only)
- Rate limits: 8 concurrent (use callWithRetry)
- Temperature: Always 1 (enforced)

### Coolify Docs
- https://coolify.io (service deployment, Docker, auto-deploy)

### Dumbarton Oaks RFP DOIT-2026-001
- 9 buildings campus-wide assessment
- Deliverables: HTML/PDF report, 10-column CSV cable inventory, capital roadmap, standards-gap analysis
- TIA-568/569/606/607 + BICSI compliance check

---

## Production Release Checklist

- [ ] All 18 bugs in spec tested & passing
- [ ] All 14 server tests passing
- [ ] All 7 client tests passing
- [ ] HEIC support detected correctly (Safari: works, Chrome: banner)
- [ ] Health endpoint responds to `curl /api/health`
- [ ] Sessions validated from disk (multi-container safe)
- [ ] CSRF hardening: Origin checks on all POSTs
- [ ] Cost guardrails: Pre-flight estimate shown, hard-stop if balance < estimate
- [ ] Rate-limit retry: 5 attempts, exponential backoff, 429/5xx handled
- [ ] Version mismatch: Red banner if STUDIO != CLIENT
- [ ] Volume persisted: Redeploy → surveys/ still there
- [ ] TLS/HTTPS enabled (Traefik configured)
- [ ] Auth password strong (not "changeme-now")
- [ ] Kimi key valid & not exposed to frontend
- [ ] GitHub webhook auto-deploy tested (if enabled)
- [ ] Backup strategy for /data volume documented
- [ ] Monitoring alerts set (health check failures, API errors, cost threshold)
- [ ] Team trained on login, survey creation, public link sharing

---

**Thinogic Survey Studio v4.2.0 — Ready for Dumbarton Oaks RFP DOIT-2026-001**
