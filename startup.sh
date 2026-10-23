#!/bin/bash

echo "🌾 Starting Agri-Guide Deployment..."

# Check if models exist
if [ ! -f "final_model/crop_recommendation_model.pkl" ] || [ ! -f "yield_model.pkl" ] || [ ! -f "crop_recommendation_model.pkl" ]; then
    echo "📦 Models not found. Training models..."
    echo "⏳ This may take 5-10 minutes on first deployment..."
    
    # Set memory-efficient Python settings
    export PYTHONHASHSEED=0
    export OMP_NUM_THREADS=1
    
    # Run normal training (optimized models should work fine now)
    python app.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Model training completed successfully!"
        echo "📁 Checking created model files:"
        if [ -d "final_model" ]; then
            ls -la final_model/
            echo "📊 Model file sizes:"
            du -h final_model/*.pkl 2>/dev/null || echo "No .pkl files found"
        else
            echo "❌ final_model directory not found!"
        fi
    else
        echo "❌ Model training failed!"
        exit 1
    fi
else
    echo "✅ Models found. Skipping training."
fi

echo "🚀 Starting web application..."
# Use gunicorn for production
if [ "$FLASK_ENV" = "development" ]; then
    python web_app.py
else
    gunicorn web_app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120
fi