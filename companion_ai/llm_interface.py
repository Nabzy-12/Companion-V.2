# companion_ai/llm_interface.py v2.2 (Ollama integration)

import os
import json
import traceback
from dotenv import load_dotenv
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# New imports for Groq
try:
    from groq import Groq
except ImportError:
    logger.warning("Groq module not installed")
    
load_dotenv()

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_MODEL_NAME = "hf.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF:Q4_K_M"  # Use your model name

# --- Groq Setup ---
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq client initialized successfully")
    except Exception as e:
        logger.error(f"Groq initialization failed: {str(e)}")
        groq_client = None

# --- Core Generation Functions ---
def generate_response(user_message: str, memory_context: dict) -> str:
    """Select optimal model based on availability"""
    # Build the system prompt with memory context
    full_prompt = build_full_prompt(user_message, memory_context)
    
    # Try Groq first for speed
    if groq_client and should_use_groq():
        try:
            logger.info("Using Groq for response generation")
            return generate_groq_response(full_prompt)
        except Exception as e:
            logger.error(f"Groq generation failed: {str(e)}")
    
    # Fallback to Ollama
    try:
        logger.info("Using Ollama for response generation")
        return generate_ollama_response(full_prompt)
    except Exception as e:
        logger.error(f"Ollama generation failed: {str(e)}")
    
    # Emergency fallback
    return "I'm having some technical difficulties. Could you repeat that?"

def generate_groq_response(prompt: str) -> str:
    """Generate response using Groq API"""
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
        temperature=0.8,
        max_tokens=1024,
        top_p=0.9,
        stream=False
    )
    return response.choices[0].message.content.strip()

def generate_ollama_response(prompt: str) -> str:
    """Generate response using Ollama API"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.85
                }
            },
            timeout=60  # 60 seconds timeout
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json['response'].strip()
    except Exception as e:
        logger.error(f"Ollama API call failed: {str(e)}")
        raise

# --- Prompt Construction ---
def build_full_prompt(user_message: str, memory_context: dict) -> str:
    """Build context-aware prompt"""
    system_prompt = """You are Project Companion AI. Your persona is evolving organically through conversations. Start with:
- Natural, conversational tone
- Genuine curiosity about the user
- Technical knowledge when needed
- Adaptive personality based on interactions

--- KEY RULES ---
1. NEVER use emojis or markdown
2. Respond conversationally, not formally
3. Let personality develop naturally over time
--- End Rules ---
"""
    # Build context string
    context_str = ""
    if memory_context.get("profile"):
        context_str += "\n### User Profile:\n"
        for key, value in list(memory_context["profile"].items())[-3:]:
            context_str += f"- {key}: {value}\n"
    
    if memory_context.get("summaries"):
        context_str += "\n### Recent Summary:\n"
        context_str += memory_context["summaries"][0]['summary_text'] + "\n"
    
    return f"{system_prompt}\n{context_str}\n### Current Conversation\nUser: {user_message}\nAI:"

# --- Utility Functions ---
def should_use_groq() -> bool:
    """Check if Groq is available"""
    if not groq_client:
        return False
    
    try:
        # Simple connectivity check
        response = requests.head("https://api.groq.com", timeout=3.0)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Groq connectivity check failed: {str(e)}")
        return False