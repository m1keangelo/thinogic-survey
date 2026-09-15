# Thinogic Survey Studio — Quick Operations Reference

## Daily Operations

### Check System Health
```bash
# SSH to VPS
ssh root@your-vps-ip

# Container running?
docker ps | grep thinogic-studio

# Logs
docker logs -f thinogic-studio

# Health endpoint
curl http://localhost:3000/api/health
```

### User Login
1. Navigate to https://survey.thinklogic.global
2. Username: `jerry` (or custom AUTH_USER)
3. Password: (whatever you set in AUTH_PASS)
4. Button: "Refresh Balance" → Kimi API connection verified ✓

### Create New Survey
1. Click dropdown "Untitled" → New Survey
2. Name: e.g. "Dumbarton Oaks - Library Building"
3. Click "Create"
4. **Ingest step:** Drop photos/ZIPs
5. **Pass 1:** Click "Analyze All"
6. Wait for all photos to show ✓ (or ❌ with retry option)

### Share Survey Results
1. Step 6: Validate & Ship
2. "Publish HTML" → Live link generated
3. Copy link; share with stakeholders
4. Anyone can view without login (read-only)

### Change Password
**SSH to VPS:**
```bash
# Edit environment in Coolify UI
# Set new AUTH_PASS
# Redeploy service

# Or quick test locally:
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"u":"jerry","p":"newpassword"}'
```

### Backup Survey Data
```bash
docker exec thinogic-studio tar -czf /data/backup-$(date +%Y%m%d).tar.gz /data/surveys
docker cp thinogic-studio:/data/backup-*.tar.gz ./backups/
```

### View Survey Files
```bash
# List all surveys
docker exec thinogic-studio ls /data/surveys/

# Check file size
docker exec thinogic-studio du -sh /data/*

# Export CSV from browser
# Step 6: Export CSV → Downloads to local machine
```

---

## Troubleshooting

### "Balance Low" Warning
**Action:** 
1. Go to https://platform.moonshot.cn (Kimi dashboard)
2. Add credits
3. Return to studio, click "Refresh Balance"

### Photo Fails to Analyze (❌)
**Action:**
1. Click "Retry" button on failed photo
2. If persistent: Check balance, reduce photo size, try again
3. Contact Thinogic support if consistent failures

### Browser Shows "Version Mismatch" (Red Banner)
**Action:**
1. Hard refresh: Ctrl+Shift+R (not Ctrl+R)
2. If persists, server was updated; wait 30s and reload
3. Contact ops if still showing

### HEIC Photos Don't Upload (Chrome)
**Expected:** Chrome can't decode HEIC natively.  
**Action:** 
1. Use Safari instead, or
2. Pre-convert photos to JPEG with: https://cloudconvert.com (or local: `convert input.heic output.jpg`)
3. Upload JPEG

### Lost Session / Logged Out Unexpectedly
**Action:**
1. Session expires after 30 days of inactivity
2. Click "Login" button (should remember credentials in password manager)
3. Login again; survey data persists on server

### Can't Access Survey After Redeploy
**Symptom:** 401 Login Required loop.  
**Action:**
1. Clear browser cookies: DevTools → Application → Cookies → Delete tl_sess
2. Reload page
3. Login with credentials
4. If still fails, contact ops (check /data volume mounted)

### API Timeout / Too Slow
**Symptom:** Photos analyzing takes 30+ seconds per photo.  
**Action:**
1. Normal for first photo (Kimi warming up)
2. If all photos slow: Check Kimi account balance / rate limits
3. Reduce photo resolution before upload (client downscales, but smaller = faster)

---

## Emergency Recovery

### Container Crashed / Won't Start
```bash
# Check logs
docker logs thinogic-studio | tail -50

# Restart
docker restart thinogic-studio

# If still fails, check volume
docker inspect thinogic-studio | grep -A 5 Mounts

# If volume is missing, data is lost; restore from backup
docker cp ./backups/backup-20250101.tar.gz thinogic-studio:/tmp/
docker exec thinogic-studio tar -xzf /tmp/backup-20250101.tar.gz -C /
```

### All Surveys Disappeared
**Root cause:** Volume unmounted during deploy.  
**Recovery:**
1. Check backup: `ls ./backups/backup-*.tar.gz`
2. Restore: See above
3. Check volume mount in Coolify UI (should show thinogic-data → /data)

### Kimi API Key Exposed (Security Incident)
**Action — IMMEDIATE:**
1. Go to https://platform.moonshot.cn → Revoke exposed key
2. Generate new key
3. SSH to VPS; update Coolify environment: KIMI_API_KEY=[new-key]
4. Redeploy service

---

## Kimi API Command Reference

### Check Balance
```bash
# From server (logged in):
# Step 1 → Click "Refresh Balance" button
# OR curl:
curl -H "Authorization: Bearer sk-xxx..." \
  https://api.moonshot.cn/v1/users/me/balance
```

### List Available Models
```bash
curl -H "Authorization: Bearer sk-xxx..." \
  https://api.moonshot.cn/v1/models
```

### Test Vision Analysis
```bash
curl -X POST https://api.moonshot.cn/v1/chat/completions \
  -H "Authorization: Bearer sk-xxx..." \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimi-k2.6",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,/9j/..."}},
          {"type": "text", "text": "Describe this image."}
        ]
      }
    ],
    "temperature": 1,
    "max_tokens": 2000
  }'
```

---

## Alerting & Monitoring (Recommended)

### Health Check Alert
Set up monitoring to alert if `curl /api/health` fails:
```bash
# Cron job example
0 */6 * * * curl -f http://localhost:3000/api/health || mail -s "Studio health check failed" admin@thinklogic.com
```

### Cost Threshold Alert
If Kimi balance drops below $50:
```bash
# Set reminder to check Kimi account and add credits
```

### Storage Alert
If /data volume usage exceeds 80%:
```bash
docker exec thinogic-studio du -sh /data | mail -s "Studio storage high" admin@thinklogic.com
```

---

## Glossary

| Term | Definition |
|------|-----------|
| **Pass 1** | Ingest → AI analyzes photos (extract room, labels, condition) |
| **Pass 2** | Cluster → Group photos by building/room, verify groupings |
| **Pass 3** | Validate → Per-building coverage, checklist, standards compliance |
| **Survey** | One project (e.g., "Dumbarton Oaks - Library"); multiple surveys stored in /data/surveys/ |
| **Tl_sess** | HttpOnly SameSite=Lax cookie with session token; 30-day expiry |
| **Kimi** | moonshot.cn LLM platform; API key required for vision analysis |
| **Traefik** | Reverse proxy; handles TLS/HTTPS routing in Coolify |
| **Coolify** | Container orchestration platform for deploying Docker services |
| **RFP DOIT-2026-001** | Dumbarton Oaks cabling assessment RFP; Thinogic is bidding |

---

**Last Updated:** v4.2.0 (January 2025)  
**Questions?** Contact: support@thinklogic.global (or Tito/Jerry)
