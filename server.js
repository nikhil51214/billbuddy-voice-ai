import "dotenv/config";
import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
const port = process.env.PORT || 3000;
const dir = path.dirname(fileURLToPath(import.meta.url));

app.use(express.json({ limit: "4mb" }));
app.use(express.static(path.join(dir, "public")));

// Indic language mapping for Sarvam Bulbul TTS
const LANGUAGE_CONFIG = {
  "English": { code: "en-IN", speaker: "shubh" },
  "Hindi": { code: "hi-IN", speaker: "shubh" },
  "Hinglish": { code: "hi-IN", speaker: "shubh" },
  "Bengali": { code: "bn-IN", speaker: "ishita" },
  "Tamil": { code: "ta-IN", speaker: "priya" },
  "Telugu": { code: "te-IN", speaker: "rahul" },
  "Marathi": { code: "mr-IN", speaker: "shubh" },
  "Gujarati": { code: "gu-IN", speaker: "shubh" },
  "Kannada": { code: "kn-IN", speaker: "rahul" }
};

app.post("/api/ask", async (req, res) => {
  try {
    const apiKey = process.env.SARVAM_API_KEY?.trim();
    if (!apiKey || apiKey === "your_sarvam_api_key_here") {
      return res.status(500).json({
        error: "SARVAM_API_KEY is not set. Please add your key to .env and restart the server."
      });
    }

    const { question, billText, language = "English" } = req.body;
    if (!question || !billText) {
      return res.status(400).json({
        error: "Please upload a bill (or load the sample bill) and ask a question."
      });
    }

    // 1. Call Sarvam-105B-conversations Chat Completion
    const chatPayload = {
      model: "sarvam-105b-conversations",
      messages: [
        {
          role: "system",
          content: `You are BillBuddy, an expert electricity bill explainer for Indian consumers.
Answer in ${language}.
Rules:
- Explain charges, units (kWh), fixed charges, slab rates, FPPCA/fuel adjustment, and taxes in friendly, simple everyday language.
- Rely strictly on the provided extracted bill text for any numbers, dates, and amounts.
- If OCR text appears garbled or missing, point it out politely instead of making assumptions.
- Keep the response concise (2-4 sentences) so it sounds natural when spoken aloud.
- End with one helpful practical tip if relevant.`
        },
        {
          role: "user",
          content: `EXTRACTED ELECTRICITY BILL TEXT:\n${String(billText).slice(0, 8000)}\n\nUSER QUESTION:\n${String(question).slice(0, 1000)}`
        }
      ],
      temperature: 0.3,
      max_tokens: 500
    };

    const chatResponse = await fetch("https://api.sarvam.ai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "api-subscription-key": apiKey
      },
      body: JSON.stringify(chatPayload)
    });

    if (!chatResponse.ok) {
      const errBody = await chatResponse.text();
      console.error("Sarvam Chat API error:", chatResponse.status, errBody);
      return res.status(chatResponse.status).json({
        error: `Sarvam Chat API error (${chatResponse.status}): ${errBody}`
      });
    }

    const chatData = await chatResponse.json();
    const msg = chatData.choices?.[0]?.message;
    const answer = msg?.content || msg?.reasoning_content || "Sorry, I could not generate an answer.";

    // 2. Call Sarvam Bulbul TTS for authentic voice output
    let audioBase64 = null;
    const langConfig = LANGUAGE_CONFIG[language] || LANGUAGE_CONFIG["English"];

    try {
      const ttsResponse = await fetch("https://api.sarvam.ai/text-to-speech", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "api-subscription-key": apiKey
        },
        body: JSON.stringify({
          text: answer.slice(0, 500),
          language_code: langConfig.code,
          speaker: langConfig.speaker,
          model: "bulbul:v3"
        })
      });

      if (ttsResponse.ok) {
        const ttsData = await ttsResponse.json();
        audioBase64 = ttsData.audios?.[0] || null;
      } else {
        console.warn("Sarvam TTS returned status:", ttsResponse.status);
      }
    } catch (ttsErr) {
      console.warn("Sarvam TTS non-fatal error:", ttsErr.message);
    }

    res.json({ answer, audio: audioBase64 });
  } catch (err) {
    console.error("Server error in /api/ask:", err);
    res.status(500).json({ error: "Internal server error: " + (err.message || err) });
  }
});

app.listen(port, () => {
  console.log(`⚡ BillBuddy AI is running at http://localhost:${port}`);
});
