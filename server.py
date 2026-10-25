#!/usr/bin/env python3
"""
BillBuddy AI — Zero-dependency Python server
Serves the website and proxies AI requests to Sarvam AI.
"""

import http.server
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

BASE_DIR = pathlib.Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
ENV_FILE = BASE_DIR / ".env"

# Helper to read .env without external libraries
def load_env():
    env_vars = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

env = load_env()
SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY") or env.get("SARVAM_API_KEY", "")
PORT = int(os.environ.get("PORT") or env.get("PORT", "3000"))

LANGUAGE_CONFIG = {
    "English": {"code": "en-IN", "speaker": "shubh"},
    "Hindi": {"code": "hi-IN", "speaker": "shubh"},
    "Hinglish": {"code": "hi-IN", "speaker": "shubh"},
    "Bengali": {"code": "bn-IN", "speaker": "ishita"},
    "Tamil": {"code": "ta-IN", "speaker": "priya"},
    "Telugu": {"code": "te-IN", "speaker": "rahul"},
    "Marathi": {"code": "mr-IN", "speaker": "shubh"},
    "Gujarati": {"code": "gu-IN", "speaker": "shubh"},
    "Kannada": {"code": "kn-IN", "speaker": "rahul"}
}

class BillBuddyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/api/ask":
            self.handle_ask()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_ask(self):
        api_key = os.environ.get("SARVAM_API_KEY") or load_env().get("SARVAM_API_KEY", "").strip()
        if not api_key or api_key == "your_sarvam_api_key_here":
            self.send_json_response(500, {
                "error": "SARVAM_API_KEY is not configured in .env. Please add your key and try again."
            })
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
        except Exception as e:
            self.send_json_response(400, {"error": "Invalid JSON body: " + str(e)})
            return

        question = data.get("question", "").strip()
        bill_text = data.get("billText", "").strip()
        language = data.get("language", "English")

        if not question or not bill_text:
            self.send_json_response(400, {"error": "Upload a bill and ask a question first."})
            return

        # 1. Call Sarvam-105B Chat Completion
        chat_url = "https://api.sarvam.ai/v1/chat/completions"
        chat_payload = {
            "model": "sarvam-105b",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are BillBuddy, an expert electricity bill explainer for Indian consumers. "
                        f"Answer in {language}. "
                        "Rules:\n"
                        "- Explain charges, units (kWh), fixed charges, slab rates, and taxes in friendly, simple everyday language.\n"
                        "- Rely strictly on the provided extracted bill text for numbers, dates, and amounts.\n"
                        "- If OCR text appears garbled or missing, point it out politely.\n"
                        "- Keep the response concise (2-4 sentences) so it sounds natural when spoken aloud.\n"
                        "- End with one helpful practical tip if relevant."
                    )
                },
                {
                    "role": "user",
                    "content": f"EXTRACTED ELECTRICITY BILL TEXT:\n{bill_text[:8000]}\n\nUSER QUESTION:\n{question[:1000]}"
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }

        req = urllib.request.Request(
            chat_url,
            data=json.dumps(chat_payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "api-subscription-key": api_key,
                "User-Agent": "BillBuddy-Voice-AI/1.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                chat_res = json.loads(resp.read().decode("utf-8"))
                choices = chat_res.get("choices", [])
                if choices:
                    msg = choices[0].get("message", {})
                    answer = msg.get("content") or msg.get("reasoning_content") or "Sorry, I could not generate an answer."
                else:
                    answer = "No response from Sarvam AI."
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8")
            self.send_json_response(e.code, {"error": f"Sarvam Chat API error ({e.code}): {err_content}"})
            return
        except Exception as e:
            self.send_json_response(500, {"error": "Sarvam Chat connection failed: " + str(e)})
            return

        # 2. Call Sarvam Bulbul TTS
        audio_base64 = None
        lang_config = LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG["English"])
        tts_url = "https://api.sarvam.ai/text-to-speech"
        tts_payload = {
            "inputs": [answer[:500]],
            "target_language_code": lang_config["code"],
            "speaker": lang_config["speaker"],
            "model": "bulbul:v4-flash"
        }

        try:
            tts_req = urllib.request.Request(
                tts_url,
                data=json.dumps(tts_payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "api-subscription-key": api_key,
                    "User-Agent": "BillBuddy-Voice-AI/1.0"
                },
                method="POST"
            )
            with urllib.request.urlopen(tts_req, timeout=20) as tts_resp:
                tts_res = json.loads(tts_resp.read().decode("utf-8"))
                audios = tts_res.get("audios", [])
                if audios:
                    audio_base64 = audios[0]
        except Exception as tts_err:
            print(f"Warning: Sarvam Bulbul TTS request failed (fallback to browser): {tts_err}", file=sys.stderr)

        self.send_json_response(200, {
            "answer": answer,
            "audio": audio_base64
        })

    def send_json_response(self, code, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

def run():
    server_address = ("", PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, BillBuddyHandler)
    print(f"⚡ BillBuddy AI is running at http://localhost:{PORT}")
    print(f"Open http://localhost:{PORT} in Chrome or your favorite browser.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down BillBuddy AI server.")

if __name__ == "__main__":
    run()
