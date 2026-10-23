# 🚀 Agri-Guide Deployment Guide

## Problem
Model files (*.pkl) are too large to push to GitHub (>100MB limit), but they're required for the web application to run.

## Solutions

---

## ✅ **Solution 1: Git LFS (Large File Storage) - RECOMMENDED**

Git LFS is designed specifically for versioning large files. It stores large files separately and keeps references in your repo.

### Setup Git LFS

1. **Install Git LFS**
   ```bash
   # Windows (using Chocolatey)
   choco install git-lfs
   
   # Or download from: https://git-lfs.github.com/
   ```

2. **Initialize Git LFS in your repository**
   ```bash
   git lfs install
   ```

3. **Track your model files**
   ```bash
   git lfs track "*.pkl"
   git lfs track "final_model/*.pkl"
   ```

4. **Update .gitignore** (remove *.pkl exclusion)
   ```bash
   # Remove or comment out the line: *.pkl
   ```

5. **Add and commit**
   ```bash
   git add .gitattributes
   git add *.pkl final_model/*.pkl
   git commit -m "Add model files with Git LFS"
   git push origin main
   ```

### Deployment Platforms Supporting Git LFS
- **Render** ✅ (Free tier available)
- **Railway** ✅ (Free tier available)
- **Heroku** ✅ (Paid plans)
- **AWS Elastic Beanstalk** ✅
- **Google Cloud Run** ✅

---

## ✅ **Solution 2: Train Models on Deployment - BEST FOR FREE HOSTING**

Train models automatically when the app starts for the first time. This is perfect for platforms with build steps.

### Implementation

1. **Create a startup script** (`startup.sh`)
   ```bash
   #!/bin/bash
   
   # Check if models exist
   if [ ! -f "final_model/crop_recommendation_model.pkl" ]; then
       echo "Models not found. Training models..."
       python app.py
   else
       echo "Models found. Skipping training."
   fi
   
   # Start the web application
   python web_app.py
   ```

2. **Update requirements.txt** (ensure all training dependencies are included)
   ```
   numpy
   pandas
   scikit-learn
   matplotlib
   seaborn
   pyyaml
   flask
   gunicorn
   ```

3. **Create Procfile** (for Heroku/Render)
   ```
   web: bash startup.sh
   ```

4. **For Railway/Render**: Set start command
   ```bash
   bash startup.sh
   ```

### Pros & Cons
✅ No large files in repo  
✅ Works on free tiers  
✅ Always uses latest training code  
⚠️ Longer initial deployment time (5-10 minutes)  
⚠️ Requires sufficient memory during build

---

## ✅ **Solution 3: Cloud Storage (S3/Google Cloud Storage)**

Store models in cloud storage and download them at runtime.

### Setup with AWS S3

1. **Upload models to S3**
   ```bash
   # Install AWS CLI
   pip install awscli
   
   # Configure AWS credentials
   aws configure
   
   # Upload models
   aws s3 cp final_model/ s3://your-bucket-name/agri-guide-models/ --recursive
   aws s3 cp *.pkl s3://your-bucket-name/agri-guide-models/
   ```

2. **Create model downloader** (`download_models.py`)
   ```python
   import os
   import boto3
   from pathlib import Path
   
   def download_models():
       """Download models from S3 if they don't exist locally."""
       s3 = boto3.client('s3')
       bucket_name = os.getenv('S3_BUCKET_NAME', 'your-bucket-name')
       
       model_files = [
           'crop_recommendation_model.pkl',
           'scaler.pkl',
           'label_encoder.pkl',
           'yield_model.pkl',
           'yield_scaler.pkl',
           'yield_feature_columns.pkl',
           'final_model/fertilizer_model.pkl',
           'final_model/soil_encoder.pkl',
           'final_model/crop_encoder.pkl',
           'final_model/fertilizer_encoder.pkl'
       ]
       
       for model_file in model_files:
           local_path = Path(model_file)
           if not local_path.exists():
               print(f"Downloading {model_file}...")
               local_path.parent.mkdir(parents=True, exist_ok=True)
               s3.download_file(bucket_name, f'agri-guide-models/{model_file}', str(local_path))
               print(f"✓ Downloaded {model_file}")
   
   if __name__ == '__main__':
       download_models()
   ```

3. **Update web_app.py** (add at the top)
   ```python
   from download_models import download_models
   
   # Download models before loading
   download_models()
   ```

4. **Set environment variables** on your deployment platform
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   S3_BUCKET_NAME=your-bucket-name
   ```

### Alternative: Google Cloud Storage
Similar approach using `google-cloud-storage` library.

---

## ✅ **Solution 4: GitHub Releases**

Upload models as release assets (up to 2GB per file).

### Steps

1. **Create a GitHub Release**
   - Go to your repo → Releases → Create new release
   - Tag: `v1.0.0`
   - Upload all `.pkl` files as assets

2. **Download models at runtime** (`download_from_release.py`)
   ```python
   import requests
   from pathlib import Path
   
   def download_models_from_release():
       """Download models from GitHub release."""
       release_url = "https://github.com/YOUR_USERNAME/YOUR_REPO/releases/download/v1.0.0"
       
       model_files = [
           'crop_recommendation_model.pkl',
           'scaler.pkl',
           'label_encoder.pkl',
           'yield_model.pkl',
           'yield_scaler.pkl',
           'yield_feature_columns.pkl'
       ]
       
       for model_file in model_files:
           local_path = Path(model_file)
           if not local_path.exists():
               print(f"Downloading {model_file}...")
               response = requests.get(f"{release_url}/{model_file}")
               local_path.write_bytes(response.content)
               print(f"✓ Downloaded {model_file}")
   
   if __name__ == '__main__':
       download_models_from_release()
   ```

---

## 🎯 **Recommended Deployment Platforms**

### 1. **Render** (RECOMMENDED - Free Tier)
- ✅ Supports Git LFS
- ✅ Free tier with 512MB RAM
- ✅ Auto-deploy from GitHub
- ✅ Easy setup

**Deploy Steps:**
1. Push code to GitHub (with or without models)
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect GitHub repo
5. Set build command: `pip install -r requirements.txt && python app.py`
6. Set start command: `gunicorn web_app:app`
7. Deploy!

### 2. **Railway** (Free $5 credit/month)
- ✅ Supports Git LFS
- ✅ Generous free tier
- ✅ Simple deployment
- ✅ Good for ML apps

### 3. **Hugging Face Spaces** (FREE for ML apps)
- ✅ Designed for ML applications
- ✅ Generous storage (50GB)
- ✅ Free GPU option
- ✅ Great for demos

**Deploy Steps:**
1. Create account on [huggingface.co](https://huggingface.co)
2. Create new Space (Gradio or Streamlit)
3. Upload your code and models
4. Add `app.py` as entry point

### 4. **PythonAnywhere** (Free tier)
- ✅ Free tier available
- ✅ Easy Flask deployment
- ⚠️ Limited storage (512MB free)
- ⚠️ Manual file upload

---

## 📋 **Quick Start: Deploy to Render (Recommended)**

### Option A: With Model Training on Deploy

1. **Update your repo**
   ```bash
   # Ensure models are in .gitignore
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Create `render.yaml`** (for easy deployment)
   ```yaml
   services:
     - type: web
       name: agri-guide
       env: python
       buildCommand: pip install -r requirements.txt && python app.py
       startCommand: gunicorn web_app:app --bind 0.0.0.0:$PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.9.0
   ```

3. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect settings
   - Click "Create Web Service"

### Option B: With Git LFS

1. **Setup Git LFS** (see Solution 1 above)

2. **Push models to GitHub**
   ```bash
   git lfs track "*.pkl"
   git add .gitattributes *.pkl final_model/*.pkl
   git commit -m "Add models with Git LFS"
   git push origin main
   ```

3. **Deploy on Render** (same as Option A)

---

## 🔧 **Production Configuration**

### Update `web_app.py` for production

```python
# Add at the end of web_app.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("Loading ML models...")
    load_models()
    print("Starting Flask application...")
    app.run(debug=debug, host='0.0.0.0', port=port)
```

### Add `gunicorn` to requirements.txt
```
numpy
pandas
scikit-learn
matplotlib
seaborn
pyyaml
flask
gunicorn
```

---

## 📊 **Comparison Table**

| Solution | Cost | Setup Difficulty | Deploy Time | Best For |
|----------|------|------------------|-------------|----------|
| Git LFS | Free-Paid | Medium | Fast | Teams, version control |
| Train on Deploy | Free | Easy | Slow (first time) | Free hosting, small projects |
| Cloud Storage (S3) | Paid | Medium | Fast | Production, scalability |
| GitHub Releases | Free | Easy | Fast | Open source, demos |

---

## 🎉 **My Recommendation**

**For your project, I recommend:**

1. **For quick demo/testing**: Use **Render with training on deploy** (Solution 2)
   - Zero cost
   - No Git LFS setup needed
   - Works immediately

2. **For production**: Use **Git LFS + Render** (Solution 1)
   - Faster deployments
   - Better version control
   - Professional approach

3. **For ML showcase**: Use **Hugging Face Spaces**
   - Free
   - Designed for ML apps
   - Great for portfolio

---

## 🆘 **Troubleshooting**

### Issue: "Out of memory during training"
**Solution**: Use a platform with more RAM (Railway, Render paid tier) or use pre-trained models from cloud storage.

### Issue: "Models not loading"
**Solution**: Check file paths are correct and models exist. Add logging to `load_models()` function.

### Issue: "Deployment timeout"
**Solution**: Increase build timeout in platform settings or use pre-trained models.

---

## 📞 **Need Help?**

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Git LFS Docs: https://git-lfs.github.com
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces

---

**Created for Agri-Guide Project**  
Last Updated: December 2024
