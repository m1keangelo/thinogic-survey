# Coolify Deployment Guide — Thinogic Survey Studio v4.2.0

**Time Required:** 15 minutes  
**Platform:** Coolify on Hostinger VPS  
**Target:** survey.thinklogic.global (or your domain)

---

## Step 1: GitHub Setup (5 minutes)

### Create GitHub Repo
```bash
# Create new repo on GitHub
# Name: thinogic-survey (or thinogic-survey-studio)
# Visibility: Private (safer for API keys)

# Clone locally
git clone https://github.com/yourusername/thinogic-survey.git
cd thinogic-survey

# Unzip v4.2.0 package
unzip thinogic-survey-v4.2.0.zip

# Check files
ls -la
# hosted_server.py ✓
# studio_hosted.html ✓
# Dockerfile ✓
# .env.example ✓
# README.md ✓
# DEPLOYMENT.md ✓
# QUICK_OPS.md ✓
# FIXES_v4.2.0.md ✓

# Push to GitHub
git add .
git commit -m "Thinogic Survey Studio v4.2.0 - production ready"
git push origin main
```

---

## Step 2: Coolify — Create Service (10 minutes)

### 2a. Access Coolify Dashboard
1. **SSH to VPS:**
   ```bash
   ssh root@your-vps-ip
   ```

2. **Open Coolify UI:**
   - URL: `https://your-vps-ip:3000` (or `http://` if not HTTPS configured yet)
   - Login with Coolify credentials

### 2b. Create New Service
1. **Coolify Dashboard → "New Service" → Docker Compose**

2. **Paste this Docker Compose:**
   ```yaml
   version: '3.8'
   services:
     thinogic:
       image: ghcr.io/yourusername/thinogic-survey:latest
       container_name: thinogic-studio
       ports:
         - "3000:8000"
       environment:
         PORT: "8000"
         DATA_DIR: "/data"
         KIMI_API_KEY: ${KIMI_API_KEY}
         AUTH_USER: ${AUTH_USER}
         AUTH_PASS: ${AUTH_PASS}
       volumes:
         - thinogic-data:/data
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 10s

   volumes:
     thinogic-data:
       driver: local
   ```

3. **Click "Save"**

### 2c. Connect GitHub Repository
1. **In Coolify service settings → "Repository"**
2. **Select:** `https://github.com/yourusername/thinogic-survey`
3. **Branch:** `main`
4. **Dockerfile Path:** `./Dockerfile`
5. **Click "Connect"**

---

## Step 3: Coolify — Set Environment Variables

### 3a. Create Production Environment
1. **In Coolify service → "Environment" tab**
2. **Select:** "Production" (dropdown)
3. **Add these variables:**

   | Variable | Value | Notes |
   |----------|-------|-------|
   | **KIMI_API_KEY** | `sk-xxx...` | Get from https://platform.moonshot.cn/api-keys |
   | **AUTH_USER** | `jerry` | Login username (can change) |
   | **AUTH_PASS** | `YourStrongPassword123!` | **Must change from default** |
   | **PORT** | `8000` | Internal port (do NOT change) |
   | **DATA_DIR** | `/data` | Persistent volume (do NOT change) |

4. **Example KIMI_API_KEY lookup:**
   - Go to https://platform.moonshot.cn
   - Login with your account
   - Settings → API Keys → Copy key starting with `sk-`
   - Paste into Coolify

5. **Click "Save"** after filling all 5 variables

### 3b. Preview Environment (Optional, Separate Setup)
1. If you want a test/preview environment before production:
   - **Select:** "Preview" environment (separate dropdown)
   - **Set different credentials** (test account, test key)
   - **Same process as Production**

---

## Step 4: Coolify — Configure Domain & SSL

### 4a. Add Domain
1. **In Coolify service → "Domains" tab**
2. **Click "Add Domain"**
3. **Enter:** `survey.thinklogic.global` (or your domain)
4. **SSL:** "Auto (Let's Encrypt)" — **check this box**
5. **Click "Save"**

### 4b. DNS Configuration (One-time Setup)
1. **Get Coolify IP:**
   - Coolify shows it in "Domains" section
   - Example: `72.60.57.137`

2. **Update DNS (GoDaddy / Namecheap / wherever your domain is):**
   - **Host:** `survey` (or subdomain name)
   - **Type:** `A`
   - **Value:** `72.60.57.137` (Coolify VPS IP)
   - **TTL:** 3600
   - **Save**

3. **Wait 5-10 minutes for DNS to propagate**

---

## Step 5: Coolify — Deploy

### 5a. Trigger Initial Deploy
1. **In Coolify service → "Deploy" tab**
2. **Click "Deploy Now"** (green button)
3. **Watch the logs:**
   ```
   Building image... ✓
   Pushing to registry... ✓
   Starting container... ✓
   Health check... ✓
   ```

4. **Expected output:**
   ```
   Thinogic hosted studio v4.2.0 on port 8000
   Auth users: jerry
   ```

### 5b. Wait for Deployment
- **Build:** ~2 min (downloads Python, installs dependencies)
- **Deploy:** ~1 min (starts container)
- **Health check:** ~30 seconds (container stable)
- **Total:** ~3-4 minutes

### 5c. Check Status
1. **Coolify Dashboard → Service Status**
   - Should show: 🟢 **Running**

2. **Manual verification:**
   ```bash
   docker ps | grep thinogic
   # Should show: thinogic-studio ... Up 2 minutes
   ```

---

## Step 6: Verify Deployment (2 minutes)

### 6a. Health Check
```bash
curl https://survey.thinklogic.global/api/health
# Expected response:
# {"ok": true, "version": "4.2.0"}
```

### 6b. Check Volume Mounted
```bash
docker exec thinogic-studio ls /data/surveys
# Should list surveys (empty on first deploy)
```

### 6c. Check Logs
```bash
docker logs -f thinogic-studio
# Should show:
# Thinogic hosted studio v4.2.0 on port 8000
# Auth users: jerry
```

### 6d. Test Login
1. **Open:** `https://survey.thinklogic.global`
2. **Username:** `jerry`
3. **Password:** (whatever you set in AUTH_PASS)
4. **Click Login**
5. **Expected:** Dashboard appears ✓

---

## Step 7: First Use Checklist

- [ ] Login successful
- [ ] Click "Refresh Balance" → Shows balance (e.g., $50.00) ✓
- [ ] Create new survey (name: "Test Survey")
- [ ] Drop a test image
- [ ] Click "Analyze All" → Photo analyzes (takes 10-20 sec)
- [ ] Result shows: "✓ 1 analyzed · 0 failed"
- [ ] Click "Logout"
- [ ] Page redirects to login ✓

---

## Troubleshooting During Deployment

### Issue: "Domain not working" (ERR_NAME_NOT_RESOLVED)
**Cause:** DNS not propagated yet.  
**Fix:**
1. Wait 5-10 minutes
2. Try incognito window (clears DNS cache)
3. `nslookup survey.thinklogic.global` should return Coolify VPS IP

### Issue: "Deployment stuck at 'Building image'"
**Cause:** Internet connection slow or Kimi API key invalid.  
**Fix:**
1. Check logs: `docker logs thinogic-studio | tail -20`
2. Verify KIMI_API_KEY is valid (starts with `sk-`)
3. Redeploy: Coolify → Service → "Deploy Now"

### Issue: "Container crashes on startup"
**Cause:** Environment variable typo or permission issue.  
**Fix:**
1. Check logs: `docker logs thinogic-studio`
2. Look for error like `KeyError: 'KIMI_API_KEY'`
3. Verify all 5 env vars set in Coolify (no empty values)
4. Redeploy

### Issue: "502 Bad Gateway" after login
**Cause:** Container not ready yet.  
**Fix:**
1. Wait 30 more seconds
2. Hard refresh: Ctrl+Shift+R
3. Check health: `curl https://survey.thinklogic.global/api/health`
4. If still fails, redeploy

### Issue: "Database/volume lost after redeploy"
**Cause:** Volume not mounted.  
**Fix:**
1. Check volume in Coolify service: `docker inspect thinogic-studio | grep -A 10 "Mounts"`
2. Should show: `/data → thinogic-data`
3. If missing, redeploy with volume in docker-compose

---

## Auto-Deploy Setup (Optional)

### Enable GitHub Auto-Deploy
1. **Coolify service → "Git" tab**
2. **Toggle: "Auto Deploy on Push"** → **ON**
3. **Copy Webhook URL** that appears
4. **Go to GitHub repo → Settings → Webhooks**
5. **Add webhook:**
   - **Payload URL:** (paste Coolify webhook URL)
   - **Events:** "Push events"
   - **Click "Add webhook"**
6. **Now, every `git push` auto-deploys** ✓

---

## Production Checklist (Before Going Live)

- [ ] Health endpoint responds: `curl /api/health` → 200 OK
- [ ] Volume persisted: `docker exec thinogic-studio ls /data/surveys`
- [ ] Login works: Username=jerry, Password=(your strong password)
- [ ] Balance shows: Click "Refresh Balance" → $X.XX appears
- [ ] HTTPS working: URL starts with `https://`
- [ ] SSL certificate valid: No browser warning
- [ ] Domain resolves: `nslookup survey.thinklogic.global` returns IP
- [ ] Logs clean: `docker logs thinogic-studio` shows no errors
- [ ] Test survey completes: Create → Ingest → Analyze → Publish
- [ ] Public link works: Share survey, open incognito (no login required)
- [ ] Team can login: Multiple users with AUTH_USERS work
- [ ] Backup strategy set: Daily backups of /data volume
- [ ] Monitoring configured: Alerts for health check failures

---

## Daily Operations (After Deployment)

### Check Health
```bash
curl https://survey.thinklogic.global/api/health
# {"ok": true, "version": "4.2.0"}
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

### Redeploy (New Changes)
```bash
# Push to GitHub
git add . && git commit -m "Updates" && git push

# If auto-deploy enabled: ✓ automatically redeploys
# If manual: Coolify → Service → "Deploy Now"
```

---

## Environment Variables Reference

| Var | Example | Required | Notes |
|-----|---------|----------|-------|
| KIMI_API_KEY | `sk-xxx...` | YES | From https://platform.moonshot.cn/api-keys |
| AUTH_USER | `jerry` | YES | Login username |
| AUTH_PASS | `YourStrongPass!` | YES | Login password (min 12 chars) |
| AUTH_USERS | `jerry:pass1,charlotte:pass2` | NO | Multi-user (overrides single-user if set) |
| PORT | `8000` | NO | Internal port; keep at 8000 |
| DATA_DIR | `/data` | NO | Persistent volume; keep at /data |

---

## Support

### Quick Troubleshooting
1. **Health check:** `curl https://survey.thinklogic.global/api/health`
2. **Logs:** `docker logs thinogic-studio | tail -20`
3. **Volume:** `docker inspect thinogic-studio | grep Mounts`
4. **Restart:** `docker restart thinogic-studio`

### Documentation
- **DEPLOYMENT.md** — Full ops guide (in repo)
- **QUICK_OPS.md** — Emergency procedures (in repo)
- **Kimi Docs:** https://platform.moonshot.cn/docs
- **Coolify Docs:** https://coolify.io

---

## Timeline Summary

| Step | Time | Action |
|------|------|--------|
| 1 | 2 min | Push to GitHub |
| 2 | 3 min | Create Coolify service + add docker-compose |
| 3 | 2 min | Set 5 environment variables |
| 4 | 1 min | Add domain + SSL |
| 5 | 4 min | Deploy + watch logs |
| 6 | 2 min | Verify health check + login |
| **Total** | **~15 min** | **Survey studio live** |

---

**You're now ready to deploy Thinogic Survey Studio v4.2.0 to production.** 🚀
