# companion_ai/memory_ai.py - Dedicated AI for memory management

import os
import json
import logging
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    logging.warning("Groq module not installed")

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Client setup
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Memory AI: Groq client initialized")
    except Exception as e:
        logger.error(f"Memory AI initialization failed: {str(e)}")

def generate_memory_response(prompt: str, temperature: float = 0.3) -> str:
    """Generate response using Groq with analytical model for memory tasks."""
    if not groq_client:
        return ""
    
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="deepseek-r1-distill-llama-70b",  # Use DeepSeek R1 for consistency
            temperature=temperature,  # Lower temperature for more consistent memory analysis
            max_tokens=512,
            top_p=0.9,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Memory AI generation failed: {str(e)}")
        return ""

def analyze_conversation_importance(user_msg: str, ai_msg: str, context: dict) -> float:
    """Analyze how important this conversation is for memory storage."""
    prompt = f"""Analyze this conversation exchange and rate its importance for long-term memory on a scale of 0.0 to 1.0.

Consider:
- Personal information revealed
- Emotional significance
- Unique insights or preferences
- Recurring themes
- Practical information

User: {user_msg}
AI: {ai_msg}

Context: {json.dumps(context, indent=2)}

Return ONLY a number between 0.0 and 1.0 representing importance:"""

    try:
        response = generate_memory_response(prompt, temperature=0.1)
        # Extract number from response
        import re
        match = re.search(r'(\d+\.?\d*)', response)
        if match:
            score = float(match.group(1))
            return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
    except:
        pass
    
    return 0.5  # Default moderate importance

def extract_smart_profile_facts(user_msg: str, ai_msg: str) -> dict:
    """Extract profile facts with confidence scoring."""
    prompt = f"""Extract personal facts about the user from this conversation. For each fact, provide a confidence score (0.0-1.0).

Return ONLY valid JSON in this exact format:
{{
    "facts": {{
        "fact_key": {{"value": "fact_value", "confidence": 0.8}}
    }}
}}

User: {user_msg}
AI: {ai_msg}

Focus on:
- Definitive personal information (high confidence)
- Preferences and interests (medium confidence)
- Implied characteristics (lower confidence)

JSON:"""

    try:
        response = generate_memory_response(prompt, temperature=0.2)
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get('facts', {})
    except Exception as e:
        logger.error(f"Profile fact extraction failed: {str(e)}")
    
    return {}

def generate_smart_summary(user_msg: str, ai_msg: str, importance_score: float) -> str:
    """Generate a contextual summary based on importance."""
    if importance_score < 0.3:
        # Low importance - brief summary
        prompt = f"""Create a brief 1-sentence summary of this low-importance exchange:
User: {user_msg}
AI: {ai_msg}

Summary:"""
    elif importance_score > 0.7:
        # High importance - detailed summary
        prompt = f"""Create a detailed 2-3 sentence summary of this important conversation, capturing key details:
User: {user_msg}
AI: {ai_msg}

Summary:"""
    else:
        # Medium importance - standard summary
        prompt = f"""Summarize this conversation in 1-2 sentences:
User: {user_msg}
AI: {ai_msg}

Summary:"""
    
    return generate_memory_response(prompt, temperature=0.4)

def categorize_insight(insight_text: str) -> str:
    """Categorize an insight for better organization."""
    prompt = f"""Categorize this insight into ONE of these categories:
- personality
- interests
- preferences
- behavior
- emotions
- relationships
- goals
- skills
- general

Insight: {insight_text}

Return ONLY the category name:"""

    response = generate_memory_response(prompt, temperature=0.1)
    
    valid_categories = ['personality', 'interests', 'preferences', 'behavior', 
                       'emotions', 'relationships', 'goals', 'skills', 'general']
    
    for category in valid_categories:
        if category in response.lower():
            return category
    
    return 'general'

def generate_contextual_insight(user_msg: str, ai_msg: str, context: dict, importance_score: float) -> str:
    """Generate insights with context awareness."""
    if importance_score < 0.4:
        return ""  # Skip insights for low-importance conversations
    
    prompt = f"""Based on this conversation and context, generate a brief insight about the user's personality, interests, or patterns.

User: {user_msg}
AI: {ai_msg}

Context: {json.dumps(context, indent=2)}
Importance: {importance_score}

Generate a concise insight (1-2 sentences) that reveals something meaningful about the user:"""

    return generate_memory_response(prompt, temperature=0.5)