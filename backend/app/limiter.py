from slowapi import Limiter
from slowapi.util import get_remote_address

# This shared instance is used by main.py and summarizer.py
limiter = Limiter(key_func=get_remote_address)