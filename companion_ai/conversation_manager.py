#!/usr/bin/env python3
"""
Conversation Manager - Handles the new separated architecture
Memory AI processes context BEFORE conversation AI responds
"""

import logging
from typing import Dict, List, Tuple
from companion_ai import memory as db
from companion_ai.llm_interface import generate_response, groq_memory_client
from companion_ai.memory_ai import analyze_conversation_importance, extract_smart_profile_facts, generate_smart_summary, generate_contextual_insight, categorize_insight

logger = logging.getLogger(__name__)

class ConversationSession:
    """Manages a conversation session with separated memory and conversation processing"""
    
    def __init__(self):
        self.conversation_history = []  # Store current session
        self.memory_context = self._load_initial_memory_context()
        
    def _load_initial_memory_context(self) -> Dict:
        """Load initial memory context from database"""
        return {
            "profile": db.get_all_profile_facts(),
            "summaries": db.get_relevant_summaries(None, 5),
            "insights": db.get_relevant_insights(None, 8)
        }
    
    def _update_memory_context_with_keywords(self, user_message: str):
        """Update memory context based on current message keywords"""
        # Extract keywords from user message
        keywords = [word.lower() for word in user_message.split() if len(word) > 3][:3]
        
        # Get relevant memories based on keywords
        if keywords:
            self.memory_context.update({
                "summaries": db.get_relevant_summaries(keywords, 5),
                "insights": db.get_relevant_insights(keywords, 8)
            })
            logger.info(f"Updated memory context with keywords: {keywords}")
    
    def process_message(self, user_message: str) -> str:
        """
        New conversation flow:
        1. Update memory context with relevant information
        2. Generate AI response with full context
        3. Store conversation for later memory processing
        """
        
        # Step 1: Update memory context based on current message
        self._update_memory_context_with_keywords(user_message)
        
        # Step 2: Generate response with enhanced context
        ai_response = generate_response(user_message, self.memory_context)
        
        # Step 3: Store conversation exchange for later processing
        self.conversation_history.append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": db.datetime.now().isoformat()
        })
        
        logger.info(f"Conversation exchange stored. Session length: {len(self.conversation_history)}")
        
        return ai_response
    
    def process_session_memory(self):
        """
        Process all conversation memory at end of session
        Uses separate memory API to avoid rate limiting
        """
        if not self.conversation_history:
            logger.info("No conversation history to process")
            return
            
        logger.info(f"Processing memory for {len(self.conversation_history)} exchanges")
        
        # Process each conversation exchange
        for exchange in self.conversation_history:
            try:
                self._process_single_exchange(exchange)
            except Exception as e:
                logger.error(f"Error processing exchange: {e}")
        
        # Clear conversation history after processing
        self.conversation_history.clear()
        logger.info("Session memory processing completed")
    
    def _process_single_exchange(self, exchange: Dict):
        """Process a single conversation exchange for memory storage"""
        user_msg = exchange["user"]
        ai_msg = exchange["ai"]
        
        # Use memory client for processing
        if not groq_memory_client:
            logger.warning("Memory client not available, skipping memory processing")
            return
        
        # Analyze importance using memory AI
        importance = self._analyze_importance_with_memory_ai(user_msg, ai_msg)
        logger.info(f"🧠 Exchange importance: {importance:.2f}")
        
        if importance > 0.2:  # Store if moderately important
            # Generate summary
            summary = self._generate_summary_with_memory_ai(user_msg, ai_msg, importance)
            if summary:
                db.add_summary(summary, importance)
            
            # Extract profile facts
            facts = self._extract_facts_with_memory_ai(user_msg, ai_msg)
            for key, data in facts.items():
                db.upsert_profile_fact(key, data['value'], data['confidence'])
            
            # Generate insights
            insight = self._generate_insight_with_memory_ai(user_msg, ai_msg, importance)
            if insight:
                category = self._categorize_insight_with_memory_ai(insight)
                db.add_insight(insight, category, importance)
        else:
            logger.info("🧠 Low importance exchange - minimal storage")
    
    def _analyze_importance_with_memory_ai(self, user_msg: str, ai_msg: str) -> float:
        """Analyze conversation importance using dedicated memory AI"""
        prompt = f"""Rate this conversation's importance for long-term memory (0.0-1.0):

CRITERIA:
- Personal info revealed (0.7-1.0)
- Emotional significance (0.6-0.9)
- Preferences/insights (0.5-0.8)
- Technical discussion (0.4-0.7)
- Casual chat (0.1-0.3)

User: {user_msg}
AI: {ai_msg}

Return only the decimal score:"""

        try:
            response = groq_memory_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast model for analysis
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            # Extract score
            import re
            score_text = response.choices[0].message.content.strip()
            match = re.search(r'(\d*\.?\d+)', score_text)
            if match:
                score = float(match.group(1))
                return min(max(score, 0.0), 1.0)
                
        except Exception as e:
            logger.error(f"Memory AI importance analysis failed: {e}")
        
        # Fallback heuristic
        combined = f"{user_msg} {ai_msg}".lower()
        if any(word in combined for word in ['favorite', 'prefer', 'remember', 'important']):
            return 0.7
        elif any(word in combined for word in ['project', 'work', 'coding']):
            return 0.5
        elif any(word in combined for word in ['hello', 'hi', 'thanks']):
            return 0.2
        return 0.4
    
    def _generate_summary_with_memory_ai(self, user_msg: str, ai_msg: str, importance: float) -> str:
        """Generate conversation summary using memory AI"""
        prompt = f"""Summarize this conversation exchange in 1-2 sentences:

User: {user_msg}
AI: {ai_msg}

Summary:"""

        try:
            response = groq_memory_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Memory AI summary generation failed: {e}")
            return ""
    
    def _extract_facts_with_memory_ai(self, user_msg: str, ai_msg: str) -> Dict:
        """Extract profile facts using memory AI"""
        prompt = f"""Extract personal facts about the user. Return as JSON with confidence scores:

User: {user_msg}
AI: {ai_msg}

Format: {{"fact_name": {{"value": "fact_value", "confidence": 0.8}}}}

JSON:"""

        try:
            response = groq_memory_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            import json
            facts_text = response.choices[0].message.content.strip()
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', facts_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            logger.error(f"Memory AI fact extraction failed: {e}")
        
        return {}
    
    def _generate_insight_with_memory_ai(self, user_msg: str, ai_msg: str, importance: float) -> str:
        """Generate user insights using memory AI"""
        if importance < 0.4:
            return ""
            
        prompt = f"""Generate a brief insight about the user based on this conversation:

User: {user_msg}
AI: {ai_msg}

Insight:"""

        try:
            response = groq_memory_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Memory AI insight generation failed: {e}")
            return ""
    
    def _categorize_insight_with_memory_ai(self, insight: str) -> str:
        """Categorize insight using memory AI"""
        prompt = f"""Categorize this insight into ONE category:
- personality
- interests  
- preferences
- skills
- general

Insight: {insight}

Category:"""

        try:
            response = groq_memory_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=20
            )
            category = response.choices[0].message.content.strip().lower()
            if category in ['personality', 'interests', 'preferences', 'skills']:
                return category
        except Exception as e:
            logger.error(f"Memory AI categorization failed: {e}")
        
        return 'general'