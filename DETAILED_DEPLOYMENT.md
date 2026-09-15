# THINOGIC SURVEY STUDIO v4.2.0 — COMPLETE DETAILED DEPLOYMENT GUIDE

**Total Time: ~30 minutes**  
**Difficulty: Beginner-friendly (no prior Coolify experience needed)**

---

# PART 1: PREPARATION (5 minutes)

## 1.1 Gather Your Credentials

**You will need these 5 things before starting:**

### 1. Kimi API Key
**How to get it:**
1. Go to: https://platform.moonshot.cn
2. Click top-right → "API Keys" (or "Settings" → "API Keys")
3. Look for your existing key OR click "Create New Key"
4. **Copy the full key** (starts with `sk-`)
   - Example: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (keep this exact)
   - ⚠️ **IMPORTANT:** Copy entire string including "sk-" prefix
5. **Paste into a safe place** (will need in 10 minutes)

### 2. Strong Password (for AUTH_PASS)
Create a strong password for login:
- **Minimum 12 characters**
- **Include:** uppercase, lowercase, number, special char
- **Example:** `Thinogic@2025Survey!`
- **Save it:** You'll need it to log in

### 3. GitHub Account & Repository
1. Go to https://github.com (create account if needed)
2. Click "+" top-right → "New repository"
3. **Repository name:** `thinogic-survey`
4. **Visibility:** Private (safer for API keys)
5. **Click "Create repository"**
6. You'll see: "Quick setup — we recommend: …" page
7. **Copy the repo URL** (looks like `https://github.com/yourusername/thinogic-survey.git`)

### 4. Coolify Access (Already Have)
- You have Coolify running on Hostinger VPS
- SSH access to VPS with `ssh root@72.60.57.137` (or your VPS IP)
- Coolify web dashboard at `https://72.60.57.137:3000` (or `http://...` if no HTTPS yet)

### 5. Domain Name (Already Have)
- Domain: `survey.thinklogic.global` (or your domain)
- Have access to DNS settings (GoDaddy / Namecheap / etc.)

---

## 1.2 Download & Verify ZIP File

1. **Download:** `thinogic-survey-v4.2.0.zip` (from output folder)
2. **Move to your working directory:**
   ```bash
   # On your laptop/local machine
   mv thinogic-survey-v4.2.0.zip ~/Desktop/  # or wherever you work
   cd ~/Desktop/
   ```

3. **Unzip and verify contents:**
   ```bash
   unzip thinogic-survey-v4.2.0.zip
   ls -la
   ```

   **You should see exactly these 8 files:**
   ```
   hosted_server.py          (13K) ← Python server
   studio_hosted.html        (24K) ← Web app
   Dockerfile                (519B) ← Container image
   .env.example              (2.7K) ← Environment template
   README.md                 (11K) ← Overview
   DEPLOYMENT.md             (15K) ← Full guide
   QUICK_OPS.md              (6.4K) ← Operations
   FIXES_v4.2.0.md           (20K) ← Technical details
   ```

   **If any file is missing:** Download ZIP again

---

# PART 2: GITHUB SETUP (5 minutes)

## 2.1 Clone Your Repository

**On your laptop/local machine:**

```bash
# Clone the empty repository you just created
git clone https://github.com/yourusername/thinogic-survey.git

# Expected output:
# Cloning into 'thinogic-survey'...
# warning: You appear to have cloned an empty repository.

cd thinogic-survey
```

---

## 2.2 Copy Files into Repository

**You now have:**
- Folder: `~/Desktop/thinogic-survey/` (empty, from GitHub)
- Files: `~/Desktop/hosted_server.py`, `studio_hosted.html`, etc. (from unzip)

**Copy the 8 files into the repository:**

```bash
# From directory where you unzipped:
cp hosted_server.py ~/Desktop/thinogic-survey/
cp studio_hosted.html ~/Desktop/thinogic-survey/
cp Dockerfile ~/Desktop/thinogic-survey/
cp .env.example ~/Desktop/thinogic-survey/
cp README.md ~/Desktop/thinogic-survey/
cp DEPLOYMENT.md ~/Desktop/thinogic-survey/
cp QUICK_OPS.md ~/Desktop/thinogic-survey/
cp FIXES_v4.2.0.md ~/Desktop/thinogic-survey/

# Verify all files are there:
cd ~/Desktop/thinogic-survey/
ls -la
```

**You should see all 8 files listed.**

---

## 2.3 Push to GitHub

**Push these files to GitHub:**

```bash
# From ~/Desktop/thinogic-survey/ directory:

# Add all files to git
git add .

# Verify what will be committed
git status
# You should see:
# On branch main
# Changes to be committed:
#   new file:   Dockerfile
#   new file:   hosted_server.py
#   new file:   etc...

# Commit the files
git commit -m "Thinogic Survey Studio v4.2.0 - production ready"

# Push to GitHub
git push origin main

# Expected output:
# Counting objects: 8, done.
# Delta compression using up to 8 threads.
# Compressing objects: 100% (8/8), done.
# Writing objects: 100% (8/8), 2.4 KiB | 1.2 MiB/s, done.
# To https://github.com/yourusername/thinogic-survey.git
#    abc1234..def5678  main -> main
```

---

## 2.4 Verify Files Are on GitHub

**Check GitHub web interface:**

1. Go to: https://github.com/yourusername/thinogic-survey
2. You should see folder icon with 8 files listed:
   ```
   ✓ hosted_server.py
   ✓ studio_hosted.html
   ✓ Dockerfile
   ✓ .env.example
   ✓ README.md
   ✓ DEPLOYMENT.md
   ✓ QUICK_OPS.md
   ✓ FIXES_v4.2.0.md
   ```

3. Click on any file to verify content is there (not empty)

**If files not showing:** 
```bash
cd ~/Desktop/thinogic-survey/
git push origin main  # Try again
```

---

# PART 3: COOLIFY SETUP (15 minutes)

## 3.1 Access Coolify Dashboard

**Open Coolify web interface:**

1. **SSH to your VPS first** (to check Coolify is running):
   ```bash
   ssh root@72.60.57.137  # Replace with your VPS IP
   # You'll be logged in to the VPS
   ```

2. **Check Coolify is running:**
   ```bash
   docker ps | grep coolify
   # Should show something like:
   # xxxxxxxx  coolify:latest  ...  Up 5 days
   ```

3. **Open Coolify in browser:**
   - URL: `https://72.60.57.137:3000`
   - Or: `http://72.60.57.137:3000` (if HTTPS not set up)
   - **Username/Password:** Your Coolify login credentials
   - Click "Login"

4. **You should see Coolify dashboard** with "Projects" and "Services" listed

---

## 3.2 Create New Service

**In Coolify dashboard:**

1. **Look for:** "New Service" button (top-right or under Projects)
   - Usually blue button saying "+ New Service" or similar

2. **Click "New Service"**

3. **A form appears with options:**
   ```
   Select service type:
   ☐ Docker
   ☐ Docker Compose  ← SELECT THIS
   ☐ Git
   ☐ etc.
   ```

4. **Click "Docker Compose"**

5. **Next screen asks for:**
   - **Service Name:** `thinogic-studio`
   - **Description (optional):** `Thinogic Survey Studio v4.2.0`
   - Click "Next" or "Continue"

---

## 3.3 Paste Docker Compose Configuration

**Coolify shows empty text editor for docker-compose.yml:**

**DELETE everything in the editor, then PASTE this exactly:**

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

**⚠️ IMPORTANT NOTES:**
- Keep `image: ghcr.io/yourusername/thinogic-survey:latest` (replace `yourusername` with your actual GitHub username, all lowercase)
- Keep `ports: - "3000:8000"` exactly (no host port 8000 direct)
- Keep all environment variables with `${...}` format
- Keep volume `thinogic-data:/data` exactly

**After pasting:**
1. Click "Save" or "Continue"
2. Coolify confirms the YAML is valid

---

## 3.4 Connect GitHub Repository

**Coolify shows "Repository" tab/section:**

1. **Click "Repository" or "Git" tab**

2. **Select repository:**
   - Dropdown or search: `thinogic-survey`
   - Click to select: `yourusername/thinogic-survey`

3. **Set Branch:**
   - Branch dropdown: Select `main`

4. **Dockerfile Path:**
   - Should auto-fill: `./Dockerfile`
   - If blank, type: `./Dockerfile`

5. **Click "Connect Repository"** or similar button

**Expected result:**
```
✓ Repository connected
✓ Branch: main
✓ Dockerfile: ./Dockerfile
```

---

## 3.5 Create Environment Variables (CRITICAL)

**Coolify shows "Environment" or "Environment Variables" tab:**

### Important: Production vs Preview
Coolify lets you set different env vars for Production and Preview environments.

**Select: "Production"** (dropdown at top, usually shows "Preview" or "Production")

### Add 5 Variables

**For each of these 5 variables, click "Add Variable" or "+" button:**

#### Variable 1: KIMI_API_KEY
- **Name:** `KIMI_API_KEY`
- **Value:** `sk-xxxxxxx...` (your full Kimi API key from step 1.1)
- **Type:** "Environment Variable" or "Secret" (if available, choose "Secret")
- Click "Add"

**⚠️ CRITICAL:**
- Copy the ENTIRE key (including `sk-` prefix)
- No spaces at start or end
- Example format: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx` (40+ characters)

#### Variable 2: AUTH_USER
- **Name:** `AUTH_USER`
- **Value:** `jerry`
- Click "Add"

(This is the login username. You can change "jerry" if you want, but "jerry" is the default.)

#### Variable 3: AUTH_PASS
- **Name:** `AUTH_PASS`
- **Value:** `Thinogic@2025Survey!` (your strong password from step 1.1)
- **Type:** "Secret" (if available)
- Click "Add"

**⚠️ CRITICAL:**
- This MUST be a strong password (min 12 chars)
- NOT "changeme-now" (that's the placeholder, you must change it)
- You'll need this to log in
- No spaces at start/end

#### Variable 4: PORT
- **Name:** `PORT`
- **Value:** `8000`
- Click "Add"

(Do NOT change this. Internal port must be 8000.)

#### Variable 5: DATA_DIR
- **Name:** `DATA_DIR`
- **Value:** `/data`
- Click "Add"

(Do NOT change this. Must be /data for volume mounting.)

### Verify All 5 Variables

After adding all 5, you should see listed:
```
✓ KIMI_API_KEY = sk-xxx... (hidden/masked)
✓ AUTH_USER = jerry
✓ AUTH_PASS = ••••••••••••• (hidden)
✓ PORT = 8000
✓ DATA_DIR = /data
```

**Click "Save Environment Variables"** or similar button.

---

## 3.6 Add Domain & SSL

**Coolify shows "Domains" or "URLs" tab:**

1. **Click "Add Domain"** or "+" button

2. **Enter domain information:**
   - **Domain:** `survey.thinklogic.global`
   - **Port:** (leave blank, or auto-fills to service port)

3. **SSL Configuration:**
   - Look for checkbox: "Auto SSL" or "Let's Encrypt" or "Auto (Let's Encrypt)"
   - **CHECK THIS BOX** ✓
   - This auto-generates free HTTPS certificate

4. **Click "Add Domain"** or "Save"

**Expected result:**
```
✓ Domain: survey.thinklogic.global
✓ SSL: Auto (Let's Encrypt)
✓ Status: Pending (will change to ✓ after deploy and DNS propagation)
```

---

## 3.7 Update DNS Records

**Before deploying, you need to point your domain to Coolify VPS:**

### Get Your VPS IP

In Coolify, the domain section shows:
- **IP Address:** `72.60.57.137` (your Coolify VPS IP)
- Copy this IP

### Update DNS at Your Domain Registrar

**Examples (adjust for your registrar):**

**GoDaddy:**
1. Go to: https://dcc.godaddy.com/manage/yourdomain.com
2. Click "DNS" tab
3. Find the `A` record for `survey` subdomain
4. Click edit (pencil icon)
5. **Value:** `72.60.57.137` (Coolify VPS IP)
6. **TTL:** 3600 (default)
7. Click "Save"

**Namecheap:**
1. Go to: Dashboard → Manage → domain.com
2. Click "Advanced DNS" tab
3. Find the `A` record for `survey` subdomain
4. Click edit (pencil icon)
5. **IPv4 Address:** `72.60.57.137`
6. Click "Save"

**For other registrars:** Search "[your registrar] update A record DNS"

### DNS Propagation Wait
- DNS takes 5-10 minutes to propagate globally
- ⚠️ **Do NOT deploy yet**
- **Wait 5 minutes, then proceed to Step 3.8**

---

## 3.8 Deploy Service

**After DNS wait + all config is done:**

1. **Coolify dashboard → Your service `thinogic-studio`**

2. **Click "Deploy" tab** (or "Deployment")

3. **Click "Deploy Now"** (large blue button)

4. **Watch the deployment logs:**
   ```
   [Building] Pulling Dockerfile...
   [Building] Building image thinogic-survey:latest...
   [Building] Pulling Python 3.12-slim base image... (2-3 min)
   [Building] ✓ Build successful
   [Pushing] Pushing to registry...
   [Pushing] ✓ Push successful
   [Deploying] Starting container...
   [Deploying] ✓ Container started
   [Health Check] Checking /api/health endpoint...
   [Health Check] ✓ Health check passing
   [Status] ✓ Service deployed successfully
   ```

   **Total time: 4-5 minutes**

5. **Expected final status:**
   ```
   Service Status: 🟢 Running
   Deployment: ✓ Latest (v4.2.0)
   Uptime: 1 minute
   ```

---

## 3.9 Verify Deployment

### Test 1: Health Endpoint

```bash
curl https://survey.thinklogic.global/api/health

# Expected response:
# {"ok": true, "version": "4.2.0"}
```

### Test 2: Volume is Mounted

```bash
docker exec thinogic-studio ls /data/surveys

# Expected output:
# (empty directory on first deploy, which is fine)
# Or: ls: cannot access '/data/surveys': No such file or directory
# (this is OK, directory gets created on first survey)
```

### Test 3: Check Logs

```bash
docker logs thinogic-studio | tail -20

# Expected output:
# Thinogic hosted studio v4.2.0 on port 8000
# Auth users: jerry
```

**If you see errors:** Skip to Troubleshooting section below.

---

# PART 4: FIRST LOGIN & VERIFICATION (3 minutes)

## 4.1 Open Survey Studio

1. **Open browser and navigate to:**
   ```
   https://survey.thinklogic.global
   ```

2. **If you see "SSL Certificate Error":**
   - This sometimes happens if Let's Encrypt cert is still generating
   - Wait 2 minutes and refresh the page
   - If persists, see Troubleshooting section

3. **You should see login screen:**
   ```
   [Thinogic logo]
   Username: [text input]
   Password: [password input]
   [Login button]
   ```

---

## 4.2 Login

1. **Username field:** Type `jerry` (or your AUTH_USER)
2. **Password field:** Type your AUTH_PASS (e.g., `Thinogic@2025Survey!`)
3. **Click "Login"**

**Expected result:**
```
Dashboard loads ✓
Left sidebar shows:
  1 Connect (step indicator)
  2 Ingest
  3 Cluster
  4 Buildings
  5 Ask Kimi
  6 Publish

Main area shows:
  "Thinogic Survey Studio"
  "v4.2.0"
  Form for Kimi configuration
```

---

## 4.3 Test Kimi Connection

1. **Click "Refresh Balance"** button (in Connect step)

2. **Expected result:**
   ```
   ✓ Green banner appears:
   💳 Balance: $50.00
   (or whatever balance you have in Kimi account)
   ```

3. **If you see "Balance Low" (red banner):**
   ```
   ⚠️ Balance: $0.50
   Add credits at https://platform.moonshot.cn
   ```
   - This is expected if your Kimi account is low on credits
   - Go to https://platform.moonshot.cn and add credits, then refresh

4. **If you see error:**
   - Check KIMI_API_KEY is correct (see Troubleshooting)

---

## 4.4 Logout Test

1. **Scroll to bottom left** → "Logout" button
2. **Click "Logout"**
3. **You should return to login screen**
4. **Click browser back button** → Should return to login (not logged in)

✓ Session management works

---

# PART 5: CREATE TEST SURVEY (2 minutes)

## 5.1 Create New Survey

1. **Click "Logout"** (you should still be on login page from above)
2. **Login again:**
   - Username: `jerry`
   - Password: your password
   - Click "Login"

3. **In dashboard, look for dropdown or button** (top-left area):
   ```
   "Untitled Survey" [dropdown ▼]
   Or: "New Survey" button
   ```

4. **Click the dropdown or "New Survey" button**

5. **Dialog appears asking for survey name:**
   ```
   Survey Name: [text input]
   [Create] [Cancel]
   ```

6. **Type survey name:**
   ```
   Library Building Assessment
   ```

7. **Click "Create"**

**Expected result:**
```
Survey created ✓
Dropdown now shows: "Library Building Assessment"
Dashboard reloads
You're now editing this survey
```

---

## 5.2 Test Upload & Analysis

1. **Click "Step 2: Ingest"** (left sidebar)

2. **You should see:**
   ```
   📸 0 · 0 analyzed · 0 failed
   
   [+ Drop Photos/Folders/ZIPs button]
   [empty file list area]
   
   [Analyze All] [Pause] [Resume] buttons
   ```

3. **Click "Drop Photos/Folders/ZIPs" button**

4. **Select a test image** from your computer:
   - JPG, PNG, or any image file
   - Size: ~1-2 MB recommended
   - Note: HEIC only works in Safari (will show warning in Chrome)

5. **Image uploads and appears in list:**
   ```
   📸 1 · 0 analyzed · 0 failed
   
   [thumbnail] test-photo.jpg
   ```

6. **Click "Analyze All" button**

7. **Photo analysis starts:**
   ```
   [status indicator changes from … to ⊙ (loading)]
   Takes 10-20 seconds
   ```

8. **After analysis completes:**
   ```
   [status changes to ✓]
   📸 1 · 1 analyzed · 0 failed ✓
   
   Completion dialog appears:
   "Pass 1 Complete"
   "1 analyzed · 0 failed · 0 pending"
   [Continue button]
   ```

9. **Click "Continue"**

**✓ System is working!**

---

## 5.3 Test Export

1. **Click "Step 6: Validate & Ship"** (left sidebar)

2. **You should see export options:**
   ```
   [📄 Download HTML]
   [🖨️ Print/PDF]
   [📊 Export CSV]
   [💾 Save Project]
   ```

3. **Click "Save Project"** (JSON export)

4. **File downloads:**
   ```
   thinogic_survey_project_v4.2.0.json
   ```

5. **Verify file saved** to your Downloads folder

**✓ Export works!**

---

# PART 6: AUTO-DEPLOY SETUP (Optional, 3 minutes)

**This makes future updates automatic: just `git push` and it deploys.**

## 6.1 GitHub Webhook

1. **Coolify dashboard → Service → "Git" tab**

2. **Look for "Auto Deploy on Push":**
   ```
   ☐ Auto Deploy on Push  ← Check this box
   ```

3. **Check the box**

4. **Coolify shows "Webhook URL":**
   ```
   Webhook URL: https://coolify.yourdomain.com/webhooks/xxxx
   (copy this entire URL)
   ```

5. **Copy webhook URL** (click copy icon or select + Ctrl+C)

## 6.2 Configure GitHub Webhook

1. **Go to GitHub repository:**
   ```
   https://github.com/yourusername/thinogic-survey
   ```

2. **Click "Settings" tab** (top-right, next to Code)

3. **Left sidebar → "Webhooks"**

4. **Click "Add webhook"** (green button)

5. **Fill in webhook form:**
   - **Payload URL:** Paste Coolify webhook URL (from step 6.1)
   - **Content type:** Application/json
   - **Events:** Select "Push events" only
   - **Active:** ✓ Check this box
   - Click "Add webhook"

6. **GitHub confirms:**
   ```
   ✓ Webhook added
   Recent Deliveries shows successful test ping
   ```

---

## 6.3 Test Auto-Deploy

**Make a test change:**

1. **On your laptop, in thinogic-survey repo:**
   ```bash
   cd ~/Desktop/thinogic-survey/
   ```

2. **Edit README.md:**
   ```bash
   echo "Test update - $(date)" >> README.md
   ```

3. **Push to GitHub:**
   ```bash
   git add README.md
   git commit -m "Test auto-deploy"
   git push origin main
   ```

4. **Watch Coolify:**
   - Dashboard → Service → Deployment tab
   - Should show "Deploying..." status
   - After 30-60 seconds, shows "✓ Deployed"

5. **Check GitHub webhook:**
   - GitHub repo → Settings → Webhooks
   - Click the webhook you just added
   - Scroll to "Recent Deliveries"
   - Should show green ✓ checkmark for your push

**✓ Auto-deploy works!**

Now, any `git push` to main will automatically redeploy. Perfect for updates!

---

# PART 7: BACKUP STRATEGY (2 minutes setup)

**Protect your survey data:**

## 7.1 Manual Backup Script

**Create file: `backup.sh` in your laptop's thinogic-survey folder:**

```bash
#!/bin/bash
# backup.sh — Backup /data volume from Coolify

VPS_IP="72.60.57.137"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="./backups"

mkdir -p $BACKUP_DIR

echo "Backing up Coolify /data volume..."
docker exec thinogic-studio tar -czf /tmp/backup-$DATE.tar.gz /data/surveys /data/images /data/public /data/sessions.json

docker cp thinogic-studio:/tmp/backup-$DATE.tar.gz $BACKUP_DIR/

echo "✓ Backup saved: $BACKUP_DIR/backup-$DATE.tar.gz"
ls -lh $BACKUP_DIR/backup-$DATE.tar.gz
```

**Make it executable:**
```bash
chmod +x backup.sh
```

## 7.2 Run Backup

**Before first production use:**
```bash
./backup.sh

# Expected output:
# Backing up Coolify /data volume...
# ✓ Backup saved: ./backups/backup-20250114-143022.tar.gz
# -rw-r--r-- 1 user staff 2.4M Jan 14 14:30 ./backups/backup-20250114-143022.tar.gz
```

## 7.3 Schedule Daily Backups (Optional)

**On VPS, add cron job:**

```bash
ssh root@72.60.57.137

# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * docker exec thinogic-studio tar -czf /tmp/backup-$(date +\%Y\%m\%d).tar.gz /data && docker cp thinogic-studio:/tmp/backup-$(date +\%Y\%m\%d).tar.gz /backups/

# Save and exit (press Ctrl+X, then Y, then Enter if using nano)
```

---

# PART 8: TROUBLESHOOTING

## Issue 1: "Connection refused" when accessing https://survey.thinklogic.global

**Cause 1: DNS not propagated**
```bash
# Check DNS resolution
nslookup survey.thinklogic.global

# Should return: 72.60.57.137 (your Coolify VPS IP)
# If returns different IP or error: DNS not propagated yet, wait 5-10 minutes
```

**Cause 2: SSL certificate not ready**
```bash
# Let's Encrypt takes up to 2 minutes after first deploy
# Solution: Wait 5 minutes and refresh browser
# Try incognito/private window (clears cache)
```

**Cause 3: Service not running**
```bash
ssh root@72.60.57.137
docker ps | grep thinogic
# Should show thinogic-studio ... Up

# If not running:
docker logs thinogic-studio | tail -20  # See error
```

---

## Issue 2: Login fails with "bad credentials"

**Check 1: AUTH_PASS is correct**
```bash
# Verify you set correct password in Coolify
# Go to Coolify → Service → Environment
# Check AUTH_PASS variable (should be masked/hidden)

# If wrong:
# 1. Click edit on AUTH_PASS
# 2. Enter correct password
# 3. Click "Save"
# 4. Redeploy service
# 5. Try login again
```

**Check 2: Browser cookies**
```
Clear browser cookies:
Chrome: Settings → Privacy → Clear browsing data → Cookies
Firefox: Preferences → Privacy → Clear history → Cookies
Safari: Develop → Clear History
Then refresh page and try login again
```

---

## Issue 3: "Balance Low" or balance doesn't show

**Check 1: KIMI_API_KEY is correct**
```bash
# Verify in Coolify → Service → Environment
# KIMI_API_KEY should be set (shown as ••••••••••)

# If blank or wrong:
# 1. Go to https://platform.moonshot.cn/api-keys
# 2. Get your API key (starts with sk-)
# 3. In Coolify, edit KIMI_API_KEY
# 4. Paste full key including sk- prefix
# 5. Click Save
# 6. Redeploy: Click "Deploy Now"
# 7. Wait 4 minutes
# 8. Try "Refresh Balance" again
```

**Check 2: Kimi account has no balance**
```
Go to: https://platform.moonshot.cn
Login → Billing or Account → Add credits
Add $10-20 to test account
Return to studio and click "Refresh Balance"
```

**Check 3: API key doesn't have permission**
```
Go to: https://platform.moonshot.cn/api-keys
Click on your API key
Verify "Status: Active"
If disabled: Click to enable
Return to studio and try again
```

---

## Issue 4: Container keeps restarting or crashing

**Check logs:**
```bash
ssh root@72.60.57.137
docker logs thinogic-studio | tail -50

# Look for error messages, copy them
# Common errors:

# Error: KeyError: 'KIMI_API_KEY'
# → KIMI_API_KEY not set in Coolify Environment
# → Go to Coolify → Service → Environment → Add KIMI_API_KEY

# Error: Address already in use
# → Port 8000 is taken
# → Change docker-compose to different port (e.g., "3001:8000")
# → Redeploy

# Error: Permission denied for /data
# → Volume mount permission issue
# → Check docker-compose has: volumes: - thinogic-data:/data
# → Redeploy
```

---

## Issue 5: "Photo analyze" returns error

**Check 1: Kimi account balance**
```
Studio → Step 1: Connect → Click "Refresh Balance"
Should show $X.XX
If $0.00: Add credits at https://platform.moonshot.cn
```

**Check 2: HEIC photos in Chrome**
```
Expected behavior: HEIC fails in Chrome with warning banner
Solution: Use Safari or convert HEIC to JPEG before uploading
```

**Check 3: Network timeout**
```
If analysis times out (>30 sec):
1. Check Kimi API status: https://platform.moonshot.cn/status
2. Try again (sometimes APIs slow)
3. Reduce image size (large photos take longer)
4. If persistent: Contact Kimi support
```

---

## Issue 6: Data lost after redeploy

**Check volume was mounted:**
```bash
docker inspect thinogic-studio | grep -A 10 "Mounts"

# Should show:
# "Mounts": [
#   {
#     "Type": "volume",
#     "Name": "thinogic-data",
#     "Source": "/var/lib/docker/volumes/thinogic-data/_data",
#     "Destination": "/data"

# If missing /data mount:
# 1. Docker-compose is wrong
# 2. Copy correct docker-compose from this guide
# 3. Go to Coolify → Service → Edit → Docker Compose
# 4. Paste corrected version with: volumes: - thinogic-data:/data
# 5. Redeploy
```

**Restore from backup (if you have one):**
```bash
# From laptop, in backups folder
docker cp ./backup-20250114.tar.gz thinogic-studio:/tmp/
docker exec thinogic-studio tar -xzf /tmp/backup-20250114.tar.gz -C /
docker restart thinogic-studio
```

---

## Issue 7: Redeploy takes too long or hangs

**This is usually normal:**
- Building Docker image: 2-3 minutes (first time)
- Pushing image: 1-2 minutes
- Starting container: 30 seconds
- Total: 4-5 minutes normal

**If it hangs beyond 10 minutes:**
```bash
# Check build logs
ssh root@72.60.57.137
docker logs thinogic-studio

# Cancel redeploy (click × or kill container)
docker stop thinogic-studio

# Try again
# Go to Coolify → Service → "Deploy Now"
```

---

## Issue 8: HTTPS/SSL certificate error

**If you see "Your connection is not private":**

**This is usually normal on first deploy:**
- Let's Encrypt cert takes 1-2 minutes to generate
- Solution: Wait 5 minutes and refresh

**If error persists:**
```bash
# Check cert status
docker exec thinogic-studio curl -v https://localhost:8000

# If cert error:
# 1. Go to Coolify → Service → Domains
# 2. Check "Auto (Let's Encrypt)" is enabled
# 3. Redeploy
# 4. Wait 10 minutes
```

---

# PART 9: PRODUCTION CHECKLIST

**Before going live with real surveys:**

## Pre-Launch Checklist
- [ ] Health check works: `curl https://survey.thinklogic.global/api/health` → 200 OK
- [ ] Login works: Username=jerry, Password=(your password)
- [ ] Balance shows: Click "Refresh Balance" → Shows $X.XX
- [ ] HTTPS works: No browser warnings, URL shows 🔒 lock
- [ ] Volume persisted: `docker exec thinogic-studio ls /data/surveys`
- [ ] Test survey created successfully
- [ ] Photo upload works
- [ ] Photo analysis works
- [ ] Export works (Save Project, Download HTML, etc.)
- [ ] Public link works (share survey, open in incognito)
- [ ] Multiple logins work (test with AUTH_USERS if set)
- [ ] Logout works
- [ ] Auto-deploy works (git push → redeploy)
- [ ] Backup strategy set up
- [ ] Team trained on login procedure

---

## Daily Monitoring
```bash
# Every morning, run:
curl https://survey.thinklogic.global/api/health
# Should return: {"ok": true, "version": "4.2.0"}

# If returns error, investigate:
ssh root@72.60.57.137
docker ps | grep thinogic  # Check if running
docker logs thinogic-studio | tail -10  # Check logs
```

---

# PART 10: NEXT STEPS

## After Deployment is Verified

1. **Tell your team:**
   ```
   Survey studio is live!
   URL: https://survey.thinklogic.global
   Username: jerry (or multi-user logins if set)
   Password: (your password)
   
   Process:
   1. Login
   2. Create new survey (name: Building name)
   3. Drop photos from building
   4. Click "Analyze All" and wait
   5. Click "Publish HTML" to share with stakeholders
   ```

2. **Create surveys for Dumbarton Oaks buildings:**
   ```
   Survey names:
   - Dumbarton Oaks Library
   - Dumbarton Oaks Main Building
   - Dumbarton Oaks Network Center
   - etc. (all 9 buildings per RFP)
   ```

3. **Upload and analyze photos:**
   - Categorize by building
   - Use ZIP files (organize by building name)
   - System auto-groups them

4. **Export final reports:**
   - Step 6: Validate & Ship
   - Download HTML (complete report)
   - Export CSV (cable inventory database)
   - Publish public links (share with Dumbarton Oaks)

---

## Support & Questions

**If you get stuck:**
1. Check appropriate Troubleshooting section above
2. Review DEPLOYMENT.md (in repo) for additional details
3. Review QUICK_OPS.md for operational procedures
4. Contact: support@thinklogic.global or Tito/Jerry

---

# SUMMARY

**You've successfully deployed:**
- ✅ Thinogic Survey Studio v4.2.0
- ✅ Python server with all 18 bugs fixed
- ✅ React-free SPA with HEIC detection
- ✅ Rate-limit retry & cost guardrails
- ✅ Persistent data storage
- ✅ HTTPS/SSL with auto-renewal
- ✅ Multi-user authentication
- ✅ Auto-deploy from GitHub
- ✅ Monitoring & backup strategy

**System is production-ready for Dumbarton Oaks RFP DOIT-2026-001.**

**Total time invested: ~30 minutes**

**Status: 🟢 LIVE**

---

**Questions? Everything is documented. You've got this. 🎯**
