# 🚀 Vercel Deployment Guide for CropPulse

CropPulse has been configured for seamless serverless deployment on **Vercel** (`@vercel/python` and Serverless Functions).

---

## 📦 What Was Configured

1. **`vercel.json`**:
   - Points build entrypoint to `web_app.py`.
   - Routes static assets (`/static/*`) directly for fast CDN caching.
   - Forwards dynamic routes to Flask WSGI.
2. **`api/index.py`**:
   - Provides a standardized modern Vercel Serverless Function entrypoint exporting `app = app`.
3. **`requirements.txt`**:
   - Updated with classical CV dependencies (`Pillow`, `scipy`, `requests`) alongside Flask, scikit-learn, etc.
   - Zero deep-learning bloat (no PyTorch/TensorFlow) keeping bundle size under Vercel's 250MB limit.
4. **Model Architecture**:
   - `final_model/disease_model.pkl` (33.6 MB) fits directly within GitHub's 100MB file limit.
   - `.gitignore` configured to ensure `final_model/*.pkl` and JSON assets are tracked.

---

## 🛠️ Deployment Steps (2 Quick Methods)

### Method 1: Deploy via GitHub & Vercel Dashboard (Recommended)

1. **Initialize Git and Commit**:
   ```bash
   git init
   git add .
   git commit -m "Deploy CropPulse with ML Disease Scanner on Vercel"
   ```

2. **Push to Your GitHub Repository**:
   ```bash
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy on Vercel**:
   - Go to [vercel.com](https://vercel.com) and log in.
   - Click **"Add New..."** → **"Project"**.
   - Select your GitHub repository.
   - Under **Build and Output Settings**, Vercel will automatically read `vercel.json`.
   - Add Environment Variables (Optional, e.g. for Gemini/Chatbot API keys if desired):
     - `GEMINI_API_KEY`: `<your_key>`
     - `FLASK_ENV`: `production`
   - Click **"Deploy"**.

Your application will be live at `https://<your-project>.vercel.app` in 2-3 minutes!

---

### Method 2: Deploy Directly via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy from project directory**:
   ```bash
   vercel
   ```
   Follow the prompts to link your project.

3. **Deploy to production**:
   ```bash
   vercel --prod
   ```

---

## 🧪 Testing Locally Before Deployment

Run the Flask server locally:
```bash
python web_app.py
```
Or run the automated integration test suite:
```bash
python tests/test_disease_integration.py
```
All routes, disease predictions, and model assets will verify automatically.
