import sys
import os

# Add root project directory to sys.path so app module imports succeed on Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
