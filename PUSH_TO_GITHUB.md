# Push to GitHub - Quick Guide

## Current Status
✅ Repository initialized
✅ All files committed
✅ Remote URL set to HTTPS
⏳ Need authentication to push

## Easiest Method: Personal Access Token

### Step 1: Create Token (2 minutes)
1. Go to: **https://github.com/settings/tokens**
2. Click **"Generate new token (classic)"**
3. Name: `health-repo-push`
4. Expiration: Choose your preference (90 days recommended)
5. **Select scope**: Check `repo` (this gives full repository access)
6. Click **"Generate token"** at bottom
7. **COPY THE TOKEN** (you won't see it again!)

### Step 2: Push
Run this command:
```powershell
git push -u origin main
```

When Windows Credential Manager pops up:
- **Username**: `buxinhealth`
- **Password**: **Paste your Personal Access Token** (NOT your GitHub password)

That's it! Your code will be pushed to GitHub.

---

## Alternative: Use Token in URL (One-time)

If you want to avoid the popup, you can embed the token in the URL temporarily:

```powershell
git remote set-url origin https://YOUR_TOKEN@github.com/buxinhealth/health.git
git push -u origin main
```

Then change it back:
```powershell
git remote set-url origin https://github.com/buxinhealth/health.git
```

---

## Troubleshooting

**If you get "403 Forbidden":**
- Make sure you're using the token, not your password
- Verify the token has `repo` scope
- Check that the token hasn't expired

**If credential manager keeps asking:**
- The token might be wrong
- Delete cached credentials: `cmdkey /delete:git:https://github.com`

---

## After Successful Push

Once pushed, you can:
1. View your code at: https://github.com/buxinhealth/health
2. Deploy to Render by connecting this repository
3. Set environment variables in Render dashboard
4. Your app will be live!

