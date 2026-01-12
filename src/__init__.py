"""
Cal.com Chatbot Package

This __init__.py file marks the 'src' directory as a Python package.

WHAT IS __init__.py?
- Makes a directory importable as a Python package
- Allows imports like: from src.chatbot import CalChatbot
- Can contain package-level initialization code (not needed here)
- Can define what's exported when someone does: from src import *

WHY IS THIS FILE MOSTLY EMPTY?
- We don't need package-level initialization
- Each module (chatbot.py, cal_api.py, etc.) is imported directly
- Keeping it simple and minimal is best practice

PYTHON PACKAGE STRUCTURE:
src/
├── __init__.py        ← This file (marks src as a package)
├── chatbot.py         ← CalChatbot class
├── cal_api.py         ← CalApiClient class
├── tools.py           ← OpenAI tool definitions
├── models.py          ← Pydantic data models
└── main.py            ← FastAPI server

Without this __init__.py, Python would not recognize src/ as a package,
and imports like "from src.chatbot import CalChatbot" would fail.
"""

# Cal.com Chatbot Package
