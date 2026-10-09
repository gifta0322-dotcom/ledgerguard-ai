from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import re

app = FastAPI(title="LedgerGuard AI - Chat & Voice Edition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class Transaction(BaseModel):
    amount: float
    description: str = ""
    sender: str = ""

class ChatMessage(BaseModel):
    message: str
    user_id: str = "benin_user"

# Simple memory
chat_history = {}

# --- CORE LOGIC ---
def analyze_fraud(tx: Transaction):
    risk = 0
    reasons = []
    desc = tx.description.lower()
    
    if tx.amount > 500000:
        risk += 60
        reasons.append(f"High amount: ₦{tx.amount}")
    if any(w in desc for w in ["urgent", "crypto", "gift card", "lottery"]):
        risk += 40
        reasons.append(f"Suspicious keywords: {tx.description}")
    if tx.sender.lower() in ["unknown", "anonymous"]:
        risk += 30
        reasons.append("Unknown sender")
    
    risk = min(risk, 100)
    status = "FRAUD SUSPECTED" if risk > 50 else "SAFE"
    return {"risk_score": risk, "status": status, "reasons": reasons}

# --- ROUTES ---
@app.get("/")
def home():
    return {
        "status": "live", 
        "message": "LedgerGuard AI v2 - Chat & Voice Ready - Benin Edition",
        "features": ["/chat", "/detect-fraud", "/transcribe", "/docs"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "time": str(datetime.now())}

@app.post("/detect-fraud")
def detect_fraud(tx: Transaction):
    result = analyze_fraud(tx)
    return {**result, "transaction": tx}

@app.post("/chat")
def chat_ai(data: ChatMessage):
    msg = data.message.lower()
    user_id = data.user_id
    
    if user_id not in chat_history:
        chat_history[user_id] = []
    chat_history[user_id].append(f"You: {data.message}")
    
    # Chat AI Logic
    if "fraud" in msg or "scam" in msg:
        reply = "I can help detect fraud! Send me transaction details: amount, description, sender. Or use /detect-fraud endpoint. What transaction looks suspicious?"
    elif "hello" in msg or "hi" in msg:
        reply = "Hello from Benin! 👋 I'm LedgerGuard AI. I can: 1. Chat with you 2. Detect fraud 3. Transcribe voice recordings. How can I help today?"
    elif "amount" in msg or "money" in msg:
        reply = "To check if it's fraud, tell me the amount, what it's for, and who sent it. Example: '1000000 urgent crypto from unknown'"
    elif "record" in msg or "voice" in msg:
        reply = "You can record voice! Use /transcribe endpoint - upload your voice note and I will convert to text and check for fraud signs."
    else:
        reply = f"You said: '{data.message}'. I'm your financial guard AI from Edo State. Ask me about fraud detection, or send a transaction to analyze!"

    chat_history[user_id].append(f"AI: {reply}")
    return {"reply": reply, "history": chat_history[user_id][-6:]}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Simulated transcription - for real Whisper AI you need API key
    # This version reads filename and simulates
    filename = file.filename
    content = await file.read()
    size_kb = len(content) / 1024
    
    # Fake transcription logic - in production use OpenAI Whisper
    simulated_text = f"Audio received: {filename} ({size_kb:.1f}KB). In real version, this would transcribe voice saying 'urgent transfer' etc."
    
    # Analyze transcribed text for fraud keywords
    fraud_keywords = ["urgent", "crypto", "transfer", "lottery", "winner"]
    detected = [k for k in fraud_keywords if k in simulated_text.lower() or k in filename.lower()]
    
    return {
        "status": "transcribed",
        "filename": filename,
        "transcribed_text": simulated_text,
        "fraud_keywords_found": detected,
        "risk_note": "HIGH RISK keywords detected in voice!" if detected else "No fraud keywords in voice",
        "next_step": "To enable real voice-to-text, add OpenAI API key and Whisper"
    }

@app.get("/history/{user_id}")
def get_history(user_id: str):
    return {"user_id": user_id, "history": chat_history.get(user_id, [])}