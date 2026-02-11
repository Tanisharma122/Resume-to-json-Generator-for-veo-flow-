# 🚀 Render Deployment Guide

## Quick Overview
This guide will walk you through deploying your Resume-to-JSON Generator to Render in about 10-15 minutes.

---

## ✅ Prerequisites (Already Done!)
- ✅ GitHub repository: `https://github.com/Tanisharma122/Resume-to-json-Generator-for-veo-flow-`
- ✅ Production configuration files created
- ✅ Application updated for production

---

## 📋 Step-by-Step Deployment

### **Step 1: Push Code to GitHub** (5 minutes)

Your code is ready on the `prod` branch. Now push it to GitHub:

```bash
# Make sure you're on the prod branch
git status

# Add all files
git add .

# Commit changes
git commit -m "Add Render deployment configuration"

# Push to GitHub
git push origin prod
```

> **Note**: If you want to deploy from the `main` branch instead, merge prod into main:
> ```bash
> git checkout main
> git merge prod
> git push origin main
> ```

---

### **Step 2: Create Render Account** (2 minutes)

1. Go to **https://render.com**
2. Click **"Get Started for Free"** or **"Sign Up"**
3. **Sign up with GitHub** (recommended - makes connecting your repo easier)
4. Authorize Render to access your GitHub account
5. Verify your email address if prompted

---

### **Step 3: Create New Web Service** (3 minutes)

1. **Dashboard**: Click the **"New +"** button in the top right
2. Select **"Web Service"**
3. **Connect Repository**:
   - Find and select: `Resume-to-json-Generator-for-veo-flow-`
   - Click **"Connect"**

---

### **Step 4: Configure Service Settings** (5 minutes)

Fill in the following settings:

#### Basic Information
- **Name**: `resume-to-json-generator` (or choose your own)
- **Region**: Choose the closest region to you:
  - 🇺🇸 Oregon (US West)
  - 🇺🇸 Ohio (US East)
  - 🇪🇺 Frankfurt (Europe)
  - 🇸🇬 Singapore (Asia)

#### Build Settings
- **Branch**: `prod` (or `main` if you merged)
- **Root Directory**: (leave blank)
- **Runtime**: `Python 3`
- **Build Command**: `sh build.sh`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

#### Instance Type
- **Plan**: Select **"Free"**

---

### **Step 5: Set Environment Variables** (2 minutes)

Scroll down to **"Environment Variables"** section and click **"Add Environment Variable"**

Add these three variables:

1. **GROQ_API_KEY**
   - Key: `GROQ_API_KEY`
   - Value: `<paste-your-groq-api-key>` (use your API key from `.env` file)

2. **GROQ_MODEL**
   - Key: `GROQ_MODEL`
   - Value: `llama-3.3-70b-versatile`

3. **PYTHON_VERSION**
   - Key: `PYTHON_VERSION`
   - Value: `3.12.0`

---

### **Step 6: Deploy!** (1 minute)

1. **Auto-Deploy**: Make sure "Auto-Deploy" is **enabled** (deploy automatically on git push)
2. Click **"Create Web Service"** button
3. Wait for deployment (first deploy takes 5-10 minutes)

---

## 🎉 Your App is Live!

Once deployment completes, you'll see:
- ✅ **Status**: "Live"
- 🌐 **URL**: Something like `https://resume-to-json-generator.onrender.com`

---

## 🧪 Testing Your Deployment

### Test 1: Health Check
Open your browser and visit:
```
https://your-app-name.onrender.com/
```
You should see the application loading!

### Test 2: API Configuration
Visit:
```
https://your-app-name.onrender.com/api/test
```
You should see a JSON response showing the API is configured.

### Test 3: Full Workflow
1. Upload a resume (PDF or DOCX)
2. Generate video description
3. Configure settings (tone, speed, clips)
4. Upload reference image
5. Generate and download JSON files

---

## ⚠️ Important Notes

### Free Tier Limitations
- **Cold Starts**: Service spins down after 15 minutes of inactivity
  - First request after idle may take 30-60 seconds
- **Runtime**: 750 hours per month (plenty for personal use)
- **Memory**: Limited (sufficient for this app)

### Keeping Service Warm (Optional)
To prevent cold starts, you can:
1. Use a service like **UptimeRobot** (free) to ping your app every 5 minutes
2. Upgrade to a paid plan ($7/month) for always-on service

---

## 🔄 Future Updates

After the initial deployment, updating is easy:

```bash
# Make your changes
git add .
git commit -m "Your update message"
git push origin prod

# Render automatically deploys! ✨
```

---

## 📱 Accessing Your Frontend

After deployment, you need to update the frontend HTML to use the production API URL.

**Option 1: Serve Frontend from Render** (Already configured!)
- Visit: `https://your-app-name.onrender.com/`
- The Flask app serves the HTML automatically

**Option 2: Separate Frontend Hosting**
- Host `index_premium_final.html` on Netlify/Vercel
- Update API URLs in the HTML to point to your Render backend

---

## 🆘 Troubleshooting

### Build Failed
- Check build logs in Render dashboard
- Verify all files are pushed to GitHub
- Check `build.sh` has execute permissions

### App Crashes on Start
- Check application logs in Render dashboard
- Verify environment variables are set correctly
- Check GROQ_API_KEY is valid

### "Module not found" errors
- Make sure all dependencies are in `requirements.txt`
- Check build logs to see if installation succeeded

### CORS Errors
- CORS is already configured in `app.py`
- If issues persist, check browser console for the exact error

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Groq Docs**: https://console.groq.com/docs

---

**Ready to deploy? Let's go! 🚀**
