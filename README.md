# ⚡ BillBuddy AI — Multilingual Electricity Bill Voice Assistant

> **Hackathon Prototype** | Powered by [Sarvam AI](https://docs.sarvam.ai) (`sarvam-105b` & `bulbul:v4-flash`)

BillBuddy AI reads electricity bills (PDF/images), extracts visible meter readings, tariffs, and charges, and lets users ask questions in their native language by voice or text. BillBuddy explains complex charges, acronyms (FPPCA, Sanctioned Load, PF), and due dates in simple everyday language with studio-quality Indian voice responses.

---

## 🌟 Features

- 📄 **Bill Reading & OCR**: Upload any JPG, PNG, WebP, or 1-page PDF electricity bill. Built-in OCR parses numbers and charges automatically.
- 🇮🇳 **Indic-First AI Explainer**: Powered by **Sarvam-105B** — specialized for Indian utility contexts, Hindi, Hinglish, and regional languages.
- 🎙 **Voice Input**: Ask questions in your native accent via microphone.
- 🔊 **Studio Voice Output**: Powered by **Sarvam Bulbul** (`bulbul:v4-flash`), delivering natural Hindi, Bengali, Tamil, Telugu, and Marathi spoken explanations with automatic rupee (`₹`) and number normalization.
- ⚡ **Zero-Dependency Runner**: Built with a lightweight Python backend (`server.py`) that runs out-of-the-box on macOS/Linux/Windows with 0 install steps, plus a Node.js Express server (`server.js`).

---

## 🚀 Quickstart (Run Locally)

### 1. Add your Sarvam API Key
Open `.env` in this directory and paste your API key:
```env
SARVAM_API_KEY=your_actual_sarvam_api_key_here
PORT=3000
```
*(Get a key from [dashboard.sarvam.ai](https://dashboard.sarvam.ai))*

### 2. Start the Server
Run using Python (zero setup required):
```bash
python3 server.py
```
*Or, if using Node.js:*
```bash
npm install
npm start
```

### 3. Open the App
Visit [http://localhost:3000](http://localhost:3000) in Chrome.
Click **⚡ Load Sample Bill**, select **Hindi**, and ask:
> *"Mera bill ₹1,735 kyu aaya hai?"*

---

## 📦 How to Push to GitHub

To upload this project to your GitHub account:

1. Create a new empty repository on [GitHub](https://github.com/new) named `billbuddy-voice-ai`.
2. In your terminal, run:
```bash
cd /Users/nikhilpratapsingh/.gemini/antigravity/scratch/billbuddy-voice-ai

# Stage and commit all files
git add .
git commit -m "Initial commit: BillBuddy AI powered by Sarvam AI"

# Rename branch to main
git branch -M main

# Link to your new repository (replace with your GitHub URL)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/billbuddy-voice-ai.git

# Push to GitHub
git push -u origin main
```

*(Note: Your `.env` file is protected by `.gitignore` and will never be committed or leaked to GitHub).*

---

## 🌐 How to Get a Free Live Link for Judges

### Option A: Free 1-Click Cloud Deployment (Render) — Recommended
1. Log in to [Render.com](https://render.com) with GitHub.
2. Click **New +** → **Web Service** → Select your `billbuddy-voice-ai` repository.
3. Render will auto-detect the configuration (`render.yaml`).
4. In the **Environment Variables** section, add:
   - `SARVAM_API_KEY` = your Sarvam API key
5. Click **Deploy Web Service**. You will receive an instant public HTTPS live link:
   `https://billbuddy-voice-ai.onrender.com`

---

### Option B: Instant Live Tunnel (Share local screen/link right now)
If you want an instant public live link to share directly with judges or test on your phone in 10 seconds:

```bash
# Using Cloudflare Tunnel (Free, no account needed)
npx cloudflared tunnel --url http://localhost:3000

# OR using localtunnel
npx localtunnel --port 3000
```
This generates a temporary public HTTPS URL (e.g., `https://happy-cat-82.loca.lt`) pointing directly to your running app!

---

## 🏗 Project Architecture

```
billbuddy-voice-ai/
├── public/
│   └── index.html       # Single-page web app with OCR & audio playback
├── server.py            # Standalone zero-dependency Python server
├── server.js            # Node.js Express server
├── package.json         # Node.js project manifest
├── render.yaml          # 1-click cloud deploy configuration
├── .env.example         # Environment variables template
├── .env                 # Local secrets (never committed)
├── .gitignore           # Git ignore rules
└── README.md            # Documentation & setup guide
```
