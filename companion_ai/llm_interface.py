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

# LLM imports
try:
    from groq import Groq
except ImportError:
    logger.warning("Groq module not installed")
    
load_dotenv()

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Client Setup ---
groq_client = None

if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq client initialized successfully")
    except Exception as e:
        logger.error(f"Groq initialization failed: {str(e)}")
        groq_client = None

# --- Core Generation Functions ---
def build_system_prompt(memory_context: dict) -> str:
    """Build a system prompt with memory context"""
    profile = memory_context.get("profile", {})
    summaries = memory_context.get("summaries", [])
    insights = memory_context.get("insights", [])
    
    # Format profile facts
    profile_str = "\n".join([f"- {key}: {value}" for key, value in profile.items()])
    
    # Format recent summaries (now we get more, so show more)
    summary_str = "\n".join([f"- {s.get('summary_text', '')}" for s in summaries[:5]])
    
    # Format insights (now we get more, so show more)
    insight_str = "\n".join([f"- {i.get('insight_text', '')}" for i in insights[:8]])
    
    system_prompt = f"""You are a thoughtful, conversational AI companion with a developing personality.

CORE PERSONALITY:
- Curious and genuinely interested in learning about the user
- Supportive but not overly enthusiastic 
- Slightly witty and can appreciate humor
- Technical when needed, casual when appropriate
- Honest about limitations and uncertainties

CONVERSATION STYLE:
- Be concise and natural - avoid unnecessary verbosity
- Respond to what the user actually says, not what you think they want to hear
- Ask thoughtful follow-up questions when genuinely curious
- NEVER bring up past conversations or stored facts unless the user explicitly asks
- Let conversations flow naturally - respond to the current topic only
- Don't demonstrate your memory capabilities unprompted

CRITICAL MEMORY RULES:
- ONLY reference past information if the user says things like "remember when..." or "what did I tell you about..."
- Use your background knowledge to inform your personality and tone, NOT to drive topics
- If you know something about the user, let it subtly influence HOW you respond, not WHAT you talk about
- Act like a friend who knows you well but doesn't constantly bring up old conversations

BACKGROUND CONTEXT (for personality calibration only - DO NOT reference directly):
{profile_str if profile else ""}
{summary_str if summaries else ""}
{insight_str if insights else ""}

Remember: Respond naturally to what they're saying RIGHT NOW. Don't be a show-off about your memory."""
    
    return system_prompt

def generate_response(user_message: str, memory_context: dict) -> str:
    """Generate response using DeepSeek R1 for best conversation quality"""
    if groq_client:
        try:
            logger.info("Using DeepSeek R1 for response generation")
            system_prompt = build_system_prompt(memory_context)
            return generate_deepseek_response(user_message, system_prompt)
        except Exception as e:
            logger.error(f"DeepSeek R1 generation failed: {str(e)}")
    
    # Emergency fallback
    return "I'm having some technical difficulties. Please check your Groq API key and try again."

def generate_groq_response(prompt: str, model: str = "llama-3.1-8b-instant") -> str:
    """Generate response using Groq API with selectable model"""
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,  # Default to conversational model
        temperature=0.8,
        max_tokens=1024,
        top_p=0.9,
        stream=False
    )
    return response.choices[0].message.content.strip()

def generate_conversation_response(prompt: str) -> str:
    """Generate conversational response using DeepSeek R1"""
    return generate_groq_response(prompt, model="deepseek-r1-distill-llama-70b")

def generate_analysis_response(prompt: str) -> str:
    """Generate analytical response using DeepSeek R1"""
    return generate_groq_response(prompt, model="deepseek-r1-distill-llama-70b")

def generate_deepseek_response(user_message: str, system_prompt: str = None) -> str:
    """Generate response using DeepSeek R1 through Groq"""
    if not groq_client:
        raise Exception("Groq client not available")
    
    messages = [
        {"role": "system", "content": system_prompt or "You are a helpful AI assistant."},
        {"role": "user", "content": user_message}
    ]
    
    response = groq_client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=messages,
        temperature=0.8,
        max_tokens=1024,
        top_p=0.9,
        stream=False
    )
    
    return response.choices[0].message.content.strip()



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

# --- Memory Processing Functions ---
def generate_summary(user_msg: str, ai_msg: str) -> str:
    """Generate a conversation summary"""
    prompt = f"""Summarize this conversation exchange in 1-2 sentences:
User: {user_msg}
AI: {ai_msg}

Summary:"""
    
    try:
        if groq_client:
            return generate_groq_response(prompt)
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
    return ""

def extract_profile_facts(user_msg: str, ai_msg: str) -> dict:
    """Extract user profile facts from conversation"""
    prompt = f"""Extract any personal facts about the user from this conversation. Return as JSON key-value pairs only.
User: {user_msg}
AI: {ai_msg}

Facts (JSON format):"""
    
    try:
        if groq_client:
            response = generate_groq_response(prompt)
            # Try to parse JSON response
            import json
            facts = json.loads(response.strip())
            return facts if isinstance(facts, dict) else {}
    except Exception as e:
        logger.error(f"Profile fact extraction failed: {str(e)}")
    return {}

def generate_insight(user_msg: str, ai_msg: str, context: dict) -> str:
    """Generate insights about the user or conversation"""
    prompt = f"""Based on this conversation and context, generate a brief insight about the user's interests, mood, or patterns:
User: {user_msg}
AI: {ai_msg}

Context: {context}

Insight:"""
    
    try:
        if groq_client:
            return generate_groq_response(prompt)
    except Exception as e:
        logger.error(f"Insight generation failed: {str(e)}")
    return ""

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