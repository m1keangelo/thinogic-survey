# READY TO DEPLOY — Thinogic Survey Studio v4.2.0

## Your Package Contents

✅ **thinogic-survey-v4.2.0.zip** (37K) — Everything you need  
Contains:
- hosted_server.py (fixed server)
- studio_hosted.html (fixed client)
- Dockerfile (Coolify deployment)
- .env.example (environment template)
- README.md (overview)
- DEPLOYMENT.md (full guide)
- QUICK_OPS.md (ops runbook)
- FIXES_v4.2.0.md (technical fixes)

---

## The 5-Minute Path to Production

### 1. GitHub Setup (2 minutes)
```bash
# Create repo on GitHub (private recommended)
# Name: thinogic-survey

git clone https://github.com/yourusername/thinogic-survey.git
cd thinogic-survey

# Unzip package
unzip thinogic-survey-v4.2.0.zip

# Push to GitHub
git add .
git commit -m "Thinogic Survey Studio v4.2.0"
git push origin main
```

### 2. Coolify Setup (10 minutes)
**Follow: COOLIFY_EXACT_STEPS.md (step-by-step)**

```
Step 1: Create service in Coolify
Step 2: Paste docker-compose (provided)
Step 3: Set 5 environment variables:
        - KIMI_API_KEY (from https://platform.moonshot.cn/api-keys)
        - AUTH_PASS (strong password, NOT "changeme-now")
        - AUTH_USER (jerry or custom)
        - PORT (8000)
        - DATA_DIR (/data)
Step 4: Add domain (survey.thinklogic.global)
Step 5: Deploy
Step 6: Verify (curl /api/health)
```

### 3. Test Login (1 minute)
```
https://survey.thinklogic.global
Username: jerry
Password: (your AUTH_PASS)
Click "Refresh Balance" → Should show $X.XX
```

**Total time: ~15 minutes**

---

## What You're Getting (Compared to v4.1.4)

### 🔧 Fixed 18 Bugs
✅ Login loops → Cookie-session auth  
✅ Server hangs → ThreadingHTTPServer  
✅ Rate limits → callWithRetry (auto-backoff)  
✅ HEIC fails → Browser detection  
✅ Cost overruns → Balance proxy + guardrails  
✅ Stale containers → Health endpoint  
✅ No multi-user → AUTH_USERS env var  
✅ No CSRF → Origin/Referer checks  
✅ Photos lost → /api/upload persistence  
✅ Version mismatches silent → /api/version + banner  
✅ Honest counts missing → Fixed  
✅ 6 more critical fixes (see FIXES_v4.2.0.md)

### 🚀 Added Deployment Infrastructure
✅ Dockerfile with health checks  
✅ .env.example template  
✅ COOLIFY_EXACT_STEPS.md (this is your Coolify guide)  
✅ DEPLOYMENT.md (troubleshooting, acceptance tests)  
✅ QUICK_OPS.md (daily operations)  

---

## File-by-File Reference

| File | Read When |
|------|-----------|
| **README.md** | First overview (5 min) |
| **COOLIFY_EXACT_STEPS.md** | Ready to deploy to Coolify (10 min) |
| **DEPLOYMENT.md** | Troubleshooting or detailed setup (reference) |
| **QUICK_OPS.md** | After deployment, daily operations (reference) |
| **FIXES_v4.2.0.md** | Want to know technical details (reference) |

---

## Critical Gotchas

### 1. KIMI_API_KEY
- **Get from:** https://platform.moonshot.cn/api-keys
- **Format:** Starts with `sk-`
- **Never expose:** Keep in Coolify env vars only (not in code/git)
- **Test:** Click "Refresh Balance" in studio → Should show $X.XX

### 2. AUTH_PASS
- **Must change:** NOT "changeme-now" (hardcoded default)
- **Minimum:** 12 characters
- **Example:** `YourStrongPass123!`
- **This is:** The login password for `jerry` (or AUTH_USER)

### 3. Domain + SSL
- **DNS:** Point your domain to Coolify VPS IP
- **SSL:** Check "Auto (Let's Encrypt)" in Coolify
- **Wait:** 5-10 minutes for DNS propagation
- **Test:** `nslookup survey.thinklogic.global` should return IP

### 4. /data Volume (CRITICAL)
- **Must be persistent:** Docker named volume (not tmpfs)
- **In docker-compose:** `thinogic-data:/data`
- **Test:** `docker exec thinogic-studio ls /data/surveys`
- **Backup:** Daily backups of /data recommended

### 5. Health Endpoint
- **Enables:** Reliable Coolify rolling updates
- **Test:** `curl https://survey.thinklogic.global/api/health`
- **Response:** `{"ok": true, "version": "4.2.0"}`
- **Without this:** Old containers don't kill on redeploy

---

## Checklist: Before You Click Deploy

- [ ] GitHub repo created & pushed with all 8 files
- [ ] Coolify account ready & SSH access to VPS
- [ ] Kimi API key obtained (starts with `sk-`)
- [ ] AUTH_PASS changed to something strong (not default)
- [ ] Domain DNS configured (survey.thinklogic.global → Coolify VPS IP)
- [ ] Docker-compose copied from COOLIFY_EXACT_STEPS.md
- [ ] 5 environment variables ready to paste in Coolify
- [ ] Coolify GitHub webhook configured (for auto-deploy)

**All set?** → Open COOLIFY_EXACT_STEPS.md and follow Step 1-7

---

## After Deployment

### Verify It's Working
```bash
# Health check
curl https://survey.thinklogic.global/api/health

# Login test
https://survey.thinklogic.global
Username: jerry
Password: (your password)
Click "Refresh Balance" → Should show $X.XX
```

### Set Up Daily Backups
```bash
# SSH to VPS and add to crontab
docker exec thinogic-studio tar -czf /data/backup-$(date +\%Y\%m\%d).tar.gz /data/surveys
```

### Enable Auto-Deploy (Optional)
In Coolify:
- Service → Git → Toggle "Auto Deploy on Push" → ON
- Copy webhook URL → Add to GitHub webhooks
- Now `git push` = auto-deploy ✓

---

## Emergency Procedures

### Container Crashed
```bash
docker logs thinogic-studio | tail -20
docker restart thinogic-studio
```

### All Data Lost
```bash
# Restore from backup
docker cp ./backups/backup-20250114.tar.gz thinogic-studio:/tmp/
docker exec thinogic-studio tar -xzf /tmp/backup-20250114.tar.gz -C /
```

### Kimi API Key Exposed
1. Revoke key: https://platform.moonshot.cn
2. Generate new key
3. Update Coolify env var
4. Redeploy

**Full emergency runbook:** QUICK_OPS.md

---

## Support

### If Something Breaks
1. Check logs: `docker logs thinogic-studio`
2. Verify health: `curl /api/health`
3. Read DEPLOYMENT.md troubleshooting section
4. Contact: support@thinklogic.global or Tito/Jerry

### Documentation
- **Coolify Docs:** https://coolify.io
- **Kimi API:** https://platform.moonshot.cn/docs
- **Thinogic:** DEPLOYMENT.md + QUICK_OPS.md (in repo)

---

## Next 30 Seconds

1. ✅ Download `thinogic-survey-v4.2.0.zip`
2. ✅ Create GitHub repo
3. ✅ Unzip + push to GitHub
4. ✅ Open `COOLIFY_EXACT_STEPS.md`
5. ✅ Follow Step 1-7 (takes 15 min)
6. ✅ Login to `https://survey.thinklogic.global`
7. ✅ Create test survey
8. ✅ You're live ✓

---

**Thinogic Survey Studio v4.2.0 is production-ready.**

**Let's win Dumbarton Oaks RFP DOIT-2026-001.** 🎯
