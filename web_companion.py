#!/usr/bin/env python3
"""
Web-based Companion AI Interface
Modern, responsive web portal for better UX
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import webbrowser
import time
import logging
from companion_ai.llm_interface import generate_response
from companion_ai import memory as db
from companion_ai.tts_manager import tts_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store conversation history
conversation_history = []

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        persona = data.get('persona', 'Aether')
        model = data.get('model', 'moonshotai/kimi-k2-instruct')
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get memory context
        memory_context = {
            "profile": db.get_all_profile_facts(),
            "summaries": db.get_latest_summary(3),
            "insights": db.get_latest_insights(3)
        }
        
        # Generate response
        ai_response = generate_response(user_message, memory_context, model, persona)
        
        # Store conversation
        from datetime import datetime
        conversation_entry = {
            "user": user_message,
            "ai": ai_response,
            "timestamp": datetime.now().isoformat(),
            "persona": persona
        }
        conversation_history.append(conversation_entry)
        
        # TTS if enabled
        if tts_manager.is_enabled:
            tts_manager.speak_text(ai_response, blocking=False)
        
        return jsonify({
            'response': ai_response,
            'timestamp': conversation_entry['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory')
def get_memory():
    """Get memory data"""
    try:
        profile = db.get_all_profile_facts()
        summaries = db.get_latest_summary(10)
        insights = db.get_latest_insights(10)
        
        return jsonify({
            'profile': profile,
            'summaries': summaries,
            'insights': insights
        })
    except Exception as e:
        logger.error(f"Memory error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/clear', methods=['POST'])
def clear_memory():
    """Clear all memory"""
    try:
        db.clear_all_memory()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Clear memory error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tts/toggle', methods=['POST'])
def toggle_tts():
    """Toggle TTS on/off"""
    try:
        tts_manager.is_enabled = not tts_manager.is_enabled
        return jsonify({'enabled': tts_manager.is_enabled})
    except Exception as e:
        logger.error(f"TTS toggle error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/change', methods=['POST'])
def change_voice():
    """Change TTS voice"""
    try:
        data = request.json
        voice_name = data.get('voice')
        
        voice_mapping = {
            "Phoebe Dragon HD": "en-US-Phoebe:DragonHDLatestNeural",
            "Ava Dragon HD": "en-US-Ava:DragonHDLatestNeural"
        }
        
        if voice_name in voice_mapping:
            success = tts_manager.set_voice(voice_mapping[voice_name])
            return jsonify({'success': success})
        else:
            return jsonify({'error': 'Invalid voice'}), 400
            
    except Exception as e:
        logger.error(f"Voice change error: {e}")
        return jsonify({'error': str(e)}), 500

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("🚀 Starting Companion AI Web Portal...")
    print("📱 Opening browser at http://localhost:5000")
    
    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Flask app
    app.run(debug=False, host='localhost', port=5000)