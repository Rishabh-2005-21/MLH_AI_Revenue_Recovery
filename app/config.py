import os
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY", ""))
LLM_API_KEY = GEMINI_API_KEY
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/recoverai.db")

