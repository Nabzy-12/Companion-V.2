# gui.py
import tkinter as tk
from tkinter import scrolledtext
from main import shutdown_event
from companion_ai.llm_interface import generate_response
from companion_ai.memory import get_all_profile_facts, get_latest_summary, get_latest_insights
import threading
import asyncio

class CompanionGUI:
    def __init__(self, root):
        self.root = root
        root.title("AI Companion - Text Mode")
        
        # Chat display
        self.chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
        self.chat_history.pack(padx=10, pady=10)
        self.chat_history.config(state=tk.DISABLED)
        
        # Input area
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.user_input = tk.Entry(self.input_frame, width=70)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5,0))
        
        # Status bar
        self.status = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Memory context
        self.memory_context = {
            "profile": get_all_profile_facts(),
            "summaries": get_latest_summary(),
            "insights": get_latest_insights()
        }
    
    def send_message(self, event=None):
        user_message = self.user_input.get().strip()
        if not user_message:
            return
            
        self.user_input.delete(0, tk.END)
        self.display_message(f"You: {user_message}", "user")
        
        # Run in background thread to avoid freezing GUI
        threading.Thread(target=self.get_ai_response, args=(user_message,)).start()
    
    def get_ai_response(self, user_message):
        self.status.config(text="Thinking...")
        
        # Get AI response
        ai_message = generate_response(user_message, self.memory_context)
        
        # Update GUI
        self.root.after(0, lambda: self.display_message(f"AI: {ai_message}", "ai"))
        self.root.after(0, lambda: self.status.config(text="Ready"))
    
    def display_message(self, message, sender):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, message + "\n\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)
        
        # Add sender-specific formatting
        if sender == "user":
            self.chat_history.tag_add("user", "end-2l linestart", "end-2l lineend")
            self.chat_history.tag_config("user", foreground="blue")
        else:
            self.chat_history.tag_add("ai", "end-2l linestart", "end-2l lineend")
            self.chat_history.tag_config("ai", foreground="green")

def run_gui():
    root = tk.Tk()
    gui = CompanionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()