#!/usr/bin/env python3
"""
Deployment readiness checker for Agri-Guide
Verifies all required files and dependencies are present.
"""

import os
import sys
from pathlib import Path
import subprocess

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists and report status."""
    if Path(dirpath).exists() and Path(dirpath).is_dir():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} (MISSING)")
        return False

def check_python_packages():
    """Check if required Python packages are installed."""
    required_packages = [
        'numpy', 'pandas', 'scikit-learn', 'matplotlib', 
        'seaborn', 'pyyaml', 'flask', 'gunicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ Python package: {package}")
        except ImportError:
            print(f"❌ Python package: {package} (NOT INSTALLED)")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_model_files():
    """Check if model files exist."""
    model_files = [
        ('crop_recommendation_model.pkl', 'Crop Recommendation Model'),
        ('scaler.pkl', 'Feature Scaler'),
        ('label_encoder.pkl', 'Label Encoder'),
        ('yield_model.pkl', 'Yield Prediction Model'),
        ('yield_scaler.pkl', 'Yield Scaler'),
        ('yield_feature_columns.pkl', 'Yield Feature Columns'),
        ('final_model/fertilizer_model.pkl', 'Fertilizer Model'),
        ('final_model/soil_encoder.pkl', 'Soil Encoder'),
        ('final_model/crop_encoder.pkl', 'Crop Encoder'),
        ('final_model/fertilizer_encoder.pkl', 'Fertilizer Encoder')
    ]
    
    models_exist = True
    missing_models = []
    
    for filepath, description in model_files:
        if not check_file_exists(filepath, description):
            models_exist = False
            missing_models.append(filepath)
    
    return models_exist, missing_models

def check_data_files():
    """Check if required data files exist."""
    data_files = [
        ('raw_data/Crop_recommendation.csv', 'Crop Recommendation Dataset'),
        ('raw_data/crop_production.csv', 'Crop Production Dataset'),
        ('Fertilizer_Prediction.csv', 'Fertilizer Prediction Dataset')
    ]
    
    data_exists = True
    missing_data = []
    
    for filepath, description in data_files:
        if not check_file_exists(filepath, description):
            data_exists = False
            missing_data.append(filepath)
    
    return data_exists, missing_data

def check_git_lfs():
    """Check if Git LFS is set up."""
    try:
        result = subprocess.run(['git', 'lfs', 'ls-files'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("✅ Git LFS: Configured and tracking files")
            print(f"   Tracked files: {len(result.stdout.strip().split())}")
            return True
        else:
            print("⚠️  Git LFS: Installed but no files tracked")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git LFS: Not installed or not configured")
        return False

def main():
    """Main deployment checker."""
    print("🌾 Agri-Guide Deployment Readiness Check")
    print("=" * 50)
    
    all_good = True
    
    # Check core application files
    print("\n📁 Core Application Files:")
    core_files = [
        ('app.py', 'Training Pipeline'),
        ('web_app.py', 'Web Application'),
        ('requirements.txt', 'Python Dependencies'),
        ('startup.sh', 'Startup Script'),
        ('Procfile', 'Process File (Heroku/Render)')
    ]
    
    for filepath, description in core_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Check directories
    print("\n📂 Required Directories:")
    directories = [
        ('agri_guide', 'Main Package'),
        ('templates', 'HTML Templates'),
        ('static', 'Static Assets'),
        ('final_model', 'Model Storage')
    ]
    
    for dirpath, description in directories:
        if not check_directory_exists(dirpath, description):
            all_good = False
    
    # Check Python packages
    print("\n🐍 Python Dependencies:")
    packages_ok, missing_packages = check_python_packages()
    if not packages_ok:
        all_good = False
        print(f"\n💡 Install missing packages: pip install {' '.join(missing_packages)}")
    
    # Check data files
    print("\n📊 Training Data:")
    data_ok, missing_data = check_data_files()
    if not data_ok:
        all_good = False
        print(f"\n💡 Missing data files: {', '.join(missing_data)}")
    
    # Check model files
    print("\n🤖 ML Models:")
    models_ok, missing_models = check_model_files()
    if not models_ok:
        print(f"\n💡 Missing models: {', '.join(missing_models)}")
        print("   Run 'python app.py' to train models")
        print("   Or set up Git LFS to track existing models")
    
    # Check Git LFS
    print("\n🔧 Git LFS Status:")
    lfs_ok = check_git_lfs()
    
    # Final assessment
    print("\n" + "=" * 50)
    if all_good and (models_ok or data_ok):
        print("🎉 READY FOR DEPLOYMENT!")
        print("\n📋 Deployment Options:")
        print("1. Render: Connect GitHub repo, auto-deploy")
        print("2. Railway: Push to GitHub, deploy with one click")
        print("3. Heroku: git push heroku main")
        print("4. Hugging Face Spaces: Upload files directly")
        
        if not models_ok and data_ok:
            print("\n⚠️  Models will be trained on first deployment (5-10 min)")
        
    else:
        print("❌ NOT READY FOR DEPLOYMENT")
        print("\n🔧 Fix the issues above before deploying")
        
        if not data_ok:
            print("   • Ensure training data files are present")
        if not packages_ok:
            print("   • Install missing Python packages")
        if not all_good:
            print("   • Ensure all core files are present")
    
    print("\n📖 See DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == '__main__':
    main()