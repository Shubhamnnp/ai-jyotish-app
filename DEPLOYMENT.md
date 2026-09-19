# 🚀 AI Jyotish SaaS & Grahalakshanam Suite — Deployment Guide

This project is fully verified, containerized, and production-ready. You can deploy it using any of the following options:

---

## 🌟 Option 1: Streamlit Community Cloud (Free 1-Click Hosting)

1. Push your repository to **GitHub** (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **"New app"**.
3. Select your repository, branch (`main`), and set the main file path:
   ```text
   src/jyotish/ui/app.py
   ```
4. Under **Advanced settings**, set your environment variable (if using Gemini AI):
   ```text
   GEMINI_API_KEY = your_gemini_api_key
   ```
5. Click **Deploy!** Your app will be live on a public URL in 2 minutes.

---

## 🐳 Option 2: Docker Container (VPS / Ubuntu / AWS / GCP / DigitalOcean)

### Using Docker Compose (Recommended)
```bash
# 1. Clone repository
git clone <repo-url>
cd "AI Jotish SaaS Project"

# 2. Build and start container in background
docker-compose up -d --build

# 3. View running app
http://your-server-ip:8501
```

### Using Plain Docker
```bash
# Build Docker image
docker build -t ai-jyotish-app .

# Run Docker container
docker run -d -p 8501:8501 --name ai_jyotish ai-jyotish-app
```

---

## ☁️ Option 3: Cloud PaaS (Render / Railway / Heroku)

1. Connect your GitHub repository to Render/Railway.
2. Select **Web Service**.
3. Build Command:
   ```bash
   pip install -r requirements.txt
   ```
4. Start Command:
   ```bash
   streamlit run src/jyotish/ui/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```

---

## 🖥️ Option 4: Linux VPS / Ubuntu Direct Hosting (Systemd Service)

### 1. Install System Dependencies & Python
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create Systemd Service (`/etc/systemd/system/jyotish.service`)
```ini
[Unit]
Description=AI Jyotish SaaS Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/AI-Jotish-SaaS-Project
ExecStart=/home/ubuntu/AI-Jotish-SaaS-Project/venv/bin/streamlit run src/jyotish/ui/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Start & Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl start jyotish
sudo systemctl enable jyotish
```

---

## 💻 Option 5: Local Desktop (Windows 1-Click Launch)

Simply double-click:
```text
run_app.bat
```
The application will start and automatically open in your default browser.

---

## 🧪 Verification & Health Check

Run the full automated test suite anytime:
```bash
# 1. 10 Kundalis & Master Calculations Verification
python tests/test_10_kundalis.py

# 2. Classical Engines & Affliction Matrix Verification
python tests/test_grahalakshanam_suite.py

# 3. Rule Engine & Astrological Algorithms Verification
python tests/test_jyotish_engine.py

# 4. REST API Verification
python tests/test_api.py
```

