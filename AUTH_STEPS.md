# GitHub Authentication Steps

## Quick Fix: Create New PAT with Full Permissions

Your current PAT doesn't have the right permissions. Let's create a new one:

### Step 1: Create New Token
1. Open: https://github.com/settings/tokens/new
2. **Note**: "Job Scraper Full Access"
3. **Expiration**: 90 days (or No expiration)
4. **Select ALL these scopes**:
   - ✅ **repo** (check the main box - this checks all sub-boxes)
   - ✅ **workflow**
   - ✅ **write:packages**
   - ✅ **delete:packages**

5. Scroll down and click **"Generate token"**
6. **COPY THE TOKEN** (starts with `ghp_` or `github_pat_`)

### Step 2: Test the Token
Open your terminal and run:

```bash
cd indeed-job-scraper

# Test if token works
curl -H "Authorization: token YOUR_NEW_TOKEN" https://api.github.com/user

# If you see your user info, the token works!
```

### Step 3: Push with New Token

```bash
cd indeed-job-scraper

# Remove old remote
git remote remove origin

# Add remote with new token (replace YOUR_NEW_TOKEN)
git remote add origin https://YOUR_NEW_TOKEN@github.com/tmiswrkspc/jobscraper.git

# Push!
git push -u origin main
```

## Alternative: Use SSH (More Secure)

### Step 1: Generate SSH Key
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter 3 times (default location, no passphrase)
```

### Step 2: Copy SSH Key
```bash
cat ~/.ssh/id_ed25519.pub
# Copy the entire output
```

### Step 3: Add to GitHub
1. Go to: https://github.com/settings/ssh/new
2. Title: "MacBook Pro"
3. Paste your key
4. Click "Add SSH key"

### Step 4: Push with SSH
```bash
cd indeed-job-scraper
git remote set-url origin git@github.com:tmiswrkspc/jobscraper.git
git push -u origin main
```

## What's Wrong with Current PAT?

The error "Permission denied" means your PAT is missing the `repo` scope. 
When creating a new token, make sure to check the **repo** checkbox!

## Need Help?

Run this to see what we're trying to push:
```bash
cd indeed-job-scraper
git log --oneline
git status
```

You should see:
- 1 commit with all your files
- Branch: main
- Ready to push!
