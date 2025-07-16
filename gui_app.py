#!/usr/bin/env python3
"""
Modern GUI for Companion AI
Features:
- Clean chat interface
- Toggle for thinking tags
- Scrollable conversation history
- Modern styling
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import re
from companion_ai.llm_interface import generate_response
from companion_ai import memory as db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Companion AI")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Settings
        self.show_thinking = tk.BooleanVar(value=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Chat.TFrame', background='#2b2b2b')
        
        # Header frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="🤖 Companion AI", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Settings frame
        settings_frame = ttk.Frame(header_frame)
        settings_frame.pack(side=tk.RIGHT)
        
        # Show thinking toggle
        thinking_check = ttk.Checkbutton(settings_frame, 
                                       text="Show AI Thinking", 
                                       variable=self.show_thinking)
        thinking_check.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='#ffffff',
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure text tags for styling
        self.chat_display.tag_configure("user", foreground="#4CAF50", font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure("ai", foreground="#2196F3", font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure("thinking", foreground="#FFC107", font=('Consolas', 9, 'italic'))
        self.chat_display.tag_configure("system", foreground="#9E9E9E", font=('Consolas', 9))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        # Message input
        self.message_entry = tk.Text(
            input_frame,
            height=3,
            font=('Consolas', 10),
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff',
            wrap=tk.WORD
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Send button
        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            width=10
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind Enter key
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
        self.message_entry.bind('<Shift-Return>', lambda e: None)  # Allow Shift+Enter for new lines
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              font=('Arial', 8), foreground='#666666')
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Welcome message
        self.add_system_message("Welcome to Companion AI! Type your message and press Ctrl+Enter to send.")
        
    def add_message(self, sender, message, tag):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp and sender
        timestamp = ""  # You can add timestamp if needed
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def add_system_message(self, message):
        """Add a system message"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"System: {message}\n\n", "system")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def process_ai_response(self, response):
        """Process AI response and handle thinking tags"""
        if not self.show_thinking.get():
            # Remove thinking tags
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            response = response.strip()
        else:
            # Style thinking tags differently
            parts = re.split(r'(<think>.*?</think>)', response, flags=re.DOTALL)
            processed_response = ""
            
            for part in parts:
                if part.startswith('<think>') and part.endswith('</think>'):
                    thinking_content = part[7:-8]  # Remove <think> tags
                    processed_response += f"\n[Thinking: {thinking_content}]\n"
                else:
                    processed_response += part
            
            response = processed_response.strip()
        
        return response
        
    def send_message(self):
        """Send user message and get AI response"""
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
            
        # Clear input
        self.message_entry.delete("1.0", tk.END)
        
        # Add user message to chat
        self.add_message("You", message, "user")
        
        # Disable send button and show thinking status
        self.send_button.config(state=tk.DISABLED)
        self.status_var.set("AI is thinking...")
        
        # Process in background thread
        def process_response():
            try:
                # Get memory context
                # Extract keywords from user message for relevant memory retrieval
                keywords = [word.lower() for word in message.split() if len(word) > 3][:3]
                
                memory_context = {
                    "profile": db.get_all_profile_facts(),
                    "summaries": db.get_relevant_summaries(keywords, 5),  # Get relevant summaries
                    "insights": db.get_relevant_insights(keywords, 8)     # Get relevant insights
                }
                
                # Generate response
                response = generate_response(message, memory_context)
                
                # Process response (handle thinking tags)
                processed_response = self.process_ai_response(response)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.handle_ai_response(message, processed_response, memory_context))
                
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                self.root.after(0, lambda: self.handle_error(str(e)))
        
        # Start background thread
        threading.Thread(target=process_response, daemon=True).start()
        
    def handle_ai_response(self, user_message, ai_response, memory_context):
        """Handle AI response in main thread"""
        self.add_message("AI", ai_response, "ai")
        self.send_button.config(state=tk.NORMAL)
        self.status_var.set("Ready")
        
        # Store conversation in memory (in background)
        def store_memory():
            try:
                from companion_ai import memory_ai
                
                # Analyze conversation importance
                importance = memory_ai.analyze_conversation_importance(user_message, ai_response, memory_context)
                print(f"🧠 Conversation importance: {importance:.2f}")
                
                if importance > 0.2:  # Store more conversations (lowered from 0.3)
                    # Generate and store summary
                    summary = memory_ai.generate_smart_summary(user_message, ai_response, importance)
                    if summary:
                        db.add_summary(summary, importance)
                    
                    # Extract and store profile facts
                    facts = memory_ai.extract_smart_profile_facts(user_message, ai_response)
                    for key, data in facts.items():
                        db.upsert_profile_fact(key, data['value'], data['confidence'])
                    
                    # Generate and store insights
                    insight = memory_ai.generate_contextual_insight(user_message, ai_response, memory_context, importance)
                    if insight:
                        category = memory_ai.categorize_insight(insight)
                        db.add_insight(insight, category, importance)
                else:
                    print("🧠 Low importance conversation - minimal memory storage")
                    
            except Exception as e:
                logger.error(f"Error storing memory: {e}")
        
        threading.Thread(target=store_memory, daemon=True).start()
        
    def handle_error(self, error_message):
        """Handle errors in main thread"""
        self.add_system_message(f"Error: {error_message}")
        self.send_button.config(state=tk.NORMAL)
        self.status_var.set("Error occurred")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = CompanionGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    main()