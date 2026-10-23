FROM python:3.10-slim

# Avoid Python writing .pyc and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
# Space default port
ENV PORT=7860

WORKDIR /app

# Install basic build tools (needed by some Python deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy your project code into the image
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Hugging Face uses
EXPOSE 7860

# Start your Flask app with gunicorn
# --workers=1 ensures only one process, so models are loaded once
CMD ["gunicorn", "web_app:app", "--bind", "0.0.0.0:7860", "--workers=1", "--timeout=600"]