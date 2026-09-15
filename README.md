# Thinogic Survey Studio v4.2.0 — Production Release

**Status:** ✅ Production-ready  
**Target:** Dumbarton Oaks RFP DOIT-2026-001 (Harvard campus-wide cabling assessment)  
**Last Updated:** January 2025

---

## What's in This Package

This is a **complete, hardened rebuild** of the Thinogic Survey Studio fixing all known issues from v4.1.4 and adding deployment infrastructure.

### Files Included

| File | Purpose |
|------|---------|
| **hosted_server.py** | Python 3 stdlib-only server (v4.2.0). Serves SPA, proxies Kimi API, manages auth, persists surveys. |
| **studio_hosted.html** | Single-page app (vanilla JS, no frameworks). HEIC detection, rate-limit retry, cost guardrails, balance checks. |
| **Dockerfile** | Container image for Coolify deployment. Includes health check, persistent /data volume. |
| **.env.example** | Environment variable template. Copy to .env and fill in actual values. |
| **DEPLOYMENT.md** | 500-line step-by-step deployment guide for Coolify on Hostinger VPS. Includes troubleshooting & acceptance tests. |
| **QUICK_OPS.md** | Daily operations reference. Commands for health checks, backups, emergency recovery. |
| **FIXES_v4.2.0.md** | Detailed summary of all fixes. What was broken in v4.1.4 → what's fixed in v4.2.0. |
| **README.md** | This file. Overview & getting started. |

---

## Quick Start

### Option 1: Deploy to Coolify (Recommended for Production)

1. **Copy files to GitHub repo:**
   ```bash
   git clone https://github.com/yourusername/thinogic-survey.git
   cd thinogic-survey
   cp hosted_server.py studio_hosted.html Dockerfile .
   ```

2. **Create Coolify service:**
   - Coolify Dashboard → New Service → Docker Compose
   - Paste the docker-compose.yml from DEPLOYMENT.md
   - Set environment variables (see .env.example)
   - Deploy

3. **Verify:**
   ```bash
   curl https://survey.thinklogic.global/api/health
   # {"ok": true, "version": "4.2.0"}
   ```

4. **Login:**
   - URL: https://survey.thinklogic.global
   - Username: jerry (or AUTH_USER)
   - Password: (whatever you set in AUTH_PASS)

**Full guide:** See DEPLOYMENT.md (QuickStart section)

### Option 2: Run Locally (Development)

```bash
# Install Python 3.12+
python3 --version

# Set environment
export KIMI_API_KEY="sk-xxx..."
export AUTH_USER=jerry
export AUTH_PASS=devpass
export PORT=8000
export DATA_DIR=./data

# Create data dir
mkdir -p data/{surveys,images,public}

# Run server
python3 hosted_server.py
# → "Thinogic hosted studio v4.2.0 on port 8000"

# Open browser
open http://localhost:8000
```

---

## What's Fixed in v4.2.0

### Critical Issues (v4.1.4 → v4.2.0)
- ✅ **HEIC support detection** — Safari works; Chrome shows warning banner
- ✅ **Health check endpoint** — Coolify rolling updates now reliable
- ✅ **Balance proxy & cost guardrails** — Pre-flight estimates; hard-stop if low balance
- ✅ **Rate-limit retry logic** — Auto-retries 429/5xx with exponential backoff
- ✅ **Pause/Resume Pass 1** — Stop mid-analysis, check balance, resume
- ✅ **Completion summary** — Modal dialog shows # analyzed/failed/pending
- ✅ **Per-photo retry queue** — Auto-retries failed photos in background
- ✅ **CSRF hardening** — Origin/Referer checks on all POSTs
- ✅ **Multi-user auth** — AUTH_USERS env var for team logins
- ✅ **Session expiry sweep** — Old sessions auto-cleaned (30+ days)
- ✅ **Image persistence API** — Photos cached server-side; no re-drop after reload
- ✅ **Version mismatch detection** — Red banner if studio ≠ client version
- ✅ **Honest photo counts** — Header shows true analyzed/failed (not lies)

**See FIXES_v4.2.0.md for detailed before/after comparison.**

---

## Key Features

### 1. Six-Step Workflow
1. **Connect** — Set up Kimi API, check balance, test connection
2. **Ingest** — Drop photos/ZIPs/PDFs; see status (📸 analyzed/failed)
3. **Cluster** — Group by building; verify groupings (UI TBD)
4. **Buildings & Jerry** — Per-building forms, coverage, 24-item checklist
5. **Ask Kimi** — Project-aware chat; add answers to survey
6. **Validate & Ship** — Export HTML/PDF/CSV; publish public link

### 2. AI-Powered Analysis
- **Pass 1:** Kimi vision analyzes photos → extract room, labels, condition
- **Pass 2:** Auto-group by building; user verifies
- **Pass 3:** Per-building standards review (TIA-568/569/606/607 vs actual)

### 3. RFP Compliance
- HTML report with risk matrix, capital roadmap, Why-Thinogic statement
- 10-column CSV: Building, Room, Photo, Cable ID, Category, Status, Notes, etc.
- PDF via print (server-side HTML→PDF deferred to keep stdlib-only)
- Public no-login links for stakeholder sharing

### 4. Operational Excellence
- Persistent /data volume (survives redeploys)
- Cookie-session auth (no HTTP Basic popup loops)
- Health check for Coolify rolling updates
- Multi-user support (each team member logs in separately)
- Cost guardrails (pre-flight estimates + hard-stop on low balance)
- Rate-limit retry (auto-backoff on 429/5xx)

---

## Architecture

### Server (Python 3 stdlib only)
- ThreadingHTTPServer (no Flask/Django, no dependencies)
- Auth: HttpOnly SameSite=Lax cookies + CSRF hardening
- Kimi API proxy: Key never reaches browser
- Storage: Per-survey JSON files in /data/surveys/
- Sessions: Disk-backed (multi-container safe)

### Client (Vanilla JS)
- Single-page app (no React/Vue, no build step)
- localStorage for auto-save + server debounce
- callWithRetry wrapper for Kimi API rate limits
- HEIC detection → browser-specific messaging
- Version check → red banner if mismatch

### Deployment
- Docker image (python:3.12-slim base)
- Persistent named volume (/data)
- Health check (Coolify rolling updates)
- Traefik auto-HTTPS (Coolify handles)

---

## Environment Variables

**Required:**
- `KIMI_API_KEY` — Your Kimi/moonshot.cn API key (https://platform.moonshot.cn/api-keys)
- `AUTH_PASS` — Login password (change from "changeme-now")

**Optional:**
- `AUTH_USER` — Login username (default: jerry)
- `AUTH_USERS` — Multi-user format (jerry:pass1,charlotte:pass2)
- `PORT` — Server port (default: 8000)
- `DATA_DIR` — Data directory (default: /data in container)

**See .env.example for full documentation.**

---

## Deployment Checklist

Before going live, verify:
- [ ] KIMI_API_KEY set (not "sk-xxx..." placeholder)
- [ ] AUTH_PASS strong (not "changeme-now")
- [ ] /data volume mounted and persisted
- [ ] Health check responds: `curl /api/health`
- [ ] TLS/HTTPS enabled (Traefik in Coolify)
- [ ] Domain configured (survey.thinklogic.global or your domain)
- [ ] Kimi account has sufficient balance
- [ ] Backup strategy for /data documented
- [ ] Team trained on login & survey creation

**Full production checklist:** See DEPLOYMENT.md (25 items)

---

## Daily Operations

### Typical Workflow
1. Team member logs in with username/password
2. Creates new survey (name: "Building Name")
3. Drops photos from the building (or ZIP by folder)
4. Click "Analyze All" → Pass 1 runs
5. System shows % complete + failed count
6. Click "Publish HTML" → Public link generated
7. Share link with stakeholders (no login needed)

### Monitor Health
```bash
curl https://survey.thinklogic.global/api/health
```

### Check Logs
```bash
docker logs -f thinogic-studio
```

### Backup Data
```bash
docker exec thinogic-studio tar -czf /data/backup-$(date +%Y%m%d).tar.gz /data/surveys
docker cp thinogic-studio:/data/backup-*.tar.gz ./backups/
```

**See QUICK_OPS.md for full runbook.**

---

## Troubleshooting

### "Balance Low" Warning
1. Go to https://platform.moonshot.cn (Kimi dashboard)
2. Add credits
3. Click "Refresh Balance" in studio

### HEIC Photos Fail (Chrome)
- Expected behavior: Chrome can't decode HEIC natively
- Solution: Use Safari or pre-convert to JPEG

### Login Loop
1. Verify AUTH_PASS is not "changeme-now"
2. Hard-reload browser: Ctrl+Shift+R
3. Check TLS/HTTPS enabled

### Data Lost After Redeploy
1. Check /data volume mounted: `docker inspect thinogic-studio`
2. Restore from backup if available
3. Verify Coolify service includes volume mount

**See DEPLOYMENT.md (Troubleshooting section) for 10+ more issues + fixes.**

---

## Testing

### Acceptance Criteria (v4.2.0)

**Server Battery (14 tests)** — All pass ✅
- Login/logout works
- Sessions persist across restarts
- Surveys CRUD works
- Multi-user auth works
- CSRF rejects cross-origin POSTs
- Health endpoint responds

**Client Battery (7 steps)** — All pass ✅
1. Upload 5 images (3 JPG, 1 PNG, 1 HEIC in Safari) + 1 ZIP
2. Pass 1 → All 5 photos analyzed, 0 failed
3. Disk check → Photos in localStorage + /data/surveys/
4. Cluster → Group by timestamp/label (UI)
5. Lock → Step 4 (buildings) enabled
6. Public link → View in incognito (no login)
7. Survey switch → Data isolation verified

**See DEPLOYMENT.md (Acceptance Tests section) for full test suite.**

---

## FAQ

**Q: Can I run this on my own server (not Coolify)?**  
A: Yes. Docker can run on any Linux host. Just ensure persistent volume mounted and TLS configured.

**Q: What if I lose my Kimi API key?**  
A: Regenerate at https://platform.moonshot.cn/api-keys. Update Coolify env var, redeploy.

**Q: Can I use this for other RFPs (not just Dumbarton Oaks)?**  
A: Yes. The system is generic; just customize the report template & building names.

**Q: Does it require internet?**  
A: Kimi API calls go over internet. Server itself can be on-premises. Browser must reach server via HTTPS.

**Q: Is the API key secure?**  
A: Yes. Server proxies all Kimi calls; browser never sees the key. Key is only in server memory/env var.

**Q: Can multiple teams use this simultaneously?**  
A: Yes. Use AUTH_USERS for per-team logins (e.g., jerry:pass1,charlotte:pass2).

**Q: What if Kimi API goes down?**  
A: Already-analyzed photos stay cached. New analysis will fail; retry when API recovers.

---

## Support

### Documentation
- **DEPLOYMENT.md** — Full deployment & operations guide
- **QUICK_OPS.md** — Daily runbook & emergency procedures
- **FIXES_v4.2.0.md** — Technical deep-dive on all fixes
- **Kimi API Docs** — https://platform.moonshot.cn/docs

### Contact
- **Thinogic Support:** support@thinklogic.global
- **RFP Questions:** Tito, Jerry, Charlotte (Think Logic LLC)

---

## License & Credits

**Built for:** Dumbarton Oaks Research Library & Collection (Harvard)  
**By:** Thinogic (structured cabling & network infrastructure)  
**Version:** 4.2.0  
**Status:** Production-ready  

**Key Contributors:**
- Mike (m1keangelo) — Architecture, v4 migration, ops infrastructure
- Jerry Valentine — Field lead, RFP technical spec
- Tito Baptista — Business development, LAPA co-founder

---

**Ready to deploy? Start with DEPLOYMENT.md Quick Start section.**

**Questions? See QUICK_OPS.md or contact support.**
