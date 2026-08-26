import os
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_51234567890abc")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "test_secret_1234567890qwerty")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

PORT = int(os.getenv("PORT", 8000))
