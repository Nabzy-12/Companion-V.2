# Companion AI v2.1

An advanced conversational AI companion with persistent memory, natural conversation flow, and evolving personality. Features a modern Copilot-inspired interface and Azure TTS integration.

## 🌟 Key Features

### 🧠 **Intelligent Memory System**
- **Persistent Memory**: Remembers conversations, preferences, and insights across sessions
- **Smart Storage**: Importance-weighted memory with automatic cleanup
- **Contextual Awareness**: Uses memory subtly to inform responses without being pushy
- **Session Logging**: Automatic conversation logs for review

### 💬 **Living AI Personality**
- **Emotional Intelligence**: Genuine emotions that respond to conversation context
- **Playful & Caring**: Mischievous personality with tsundere elements
- **Adaptive Responses**: Reads the room and matches your energy naturally
- **Evolving Bond**: Grows closer through shared experiences

### 🖥️ **Modern Copilot-Style Interface**
- **Clean Design**: GitHub Copilot-inspired dark theme
- **Quick Actions**: One-click conversation starters and tools
- **Responsive Layout**: Adapts to different window sizes
- **Keyboard Shortcuts**: Enter to send, Ctrl+N to clear, Escape to focus input

### 🎤 **Azure TTS Integration**
- **High-Quality Voices**: Phoebe and Ava Dragon HD Latest voices
- **Natural Speech**: Mood-based voice adjustments and natural pacing
- **Smart Text Processing**: Handles abbreviations and emotional delivery
- **Voice Controls**: Easy toggle and voice selection

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (free tier available)
- Optional: Azure Speech Services for voice features

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Companion-V.2.git
   cd Companion-V.2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   AZURE_SPEECH_KEY=your_azure_speech_key_here  # Optional
   AZURE_SPEECH_REGION=your_azure_region_here   # Optional
   ```

4. **Run the application**
   ```bash
   # Modern Copilot-Style GUI (Recommended)
   python copilot_gui.py
   
   # Alternative interfaces
   python gui_app.py    # Original modern GUI
   python gui.py        # Text interface
   python main.py       # Voice-enabled mode
   ```

## 🎯 Usage

### GUI Interface
- **Send Messages**: Type and press Ctrl+Enter
- **Toggle Thinking**: Check "Show AI Thinking" to see reasoning process
- **Natural Conversation**: Just chat normally - memory works in the background

### Memory Commands
- `memory` - View your stored profile
- `stats` - See memory statistics
- `cleanup` - Run smart memory cleanup
- `clear` - Clear the screen

### Memory Behavior
- **Automatic**: Stores important conversations and insights
- **Subtle**: Uses memory to inform personality, not drive topics
- **Contextual**: Retrieves relevant memories based on current conversation
- **Respectful**: Only references past conversations when you bring them up

## 🏗️ Architecture

```
Companion-V.2/
├── companion_ai/           # Core AI modules
│   ├── llm_interface.py   # DeepSeek R1 integration
│   ├── memory.py          # Database operations
│   ├── memory_ai.py       # AI-powered memory processing
│   ├── tts_manager.py     # Azure TTS integration
│   └── __init__.py
├── data/                  # SQLite database storage
│   └── companion_ai.db    # Persistent memory database
├── copilot_gui.py        # Modern Copilot-Style GUI (Recommended)
├── gui_app.py            # Original modern GUI
├── gui.py                # Text interface
├── main.py               # Voice-enabled interface
├── calibrate_mic.py      # Audio calibration
├── list_audio_devices.py # Audio device management
└── test_all_systems.py   # System testing
```

## 🧠 Memory System Details

### Storage Types
- **Profile Facts**: Personal information and preferences
- **Conversation Summaries**: Important conversation highlights
- **Insights**: AI-generated observations about user patterns

### Retrieval Strategy
1. **Keyword Extraction**: Identifies relevant terms from current message
2. **Relevance Search**: Finds memories containing those keywords
3. **Importance Weighting**: Prioritizes high-relevance memories
4. **Fallback**: Uses recent high-importance memories if no matches

### Smart Features
- **Deduplication**: Prevents storing similar information multiple times
- **Aging**: Gradually reduces relevance of old, unused memories
- **Consolidation**: Merges similar memories to reduce redundancy
- **Cleanup**: Automatically removes very old, low-relevance data

## 🔧 Configuration

### Memory Settings
- **Importance Threshold**: 0.2 (stores more conversations)
- **Summary Limit**: 5 most relevant summaries
- **Insight Limit**: 8 most relevant insights
- **Cleanup Frequency**: Automatic on low importance

### AI Settings
- **Model**: DeepSeek R1 (consistent across all functions)
- **Temperature**: 0.8 (balanced creativity/consistency)
- **Max Tokens**: 1024 (sufficient for detailed responses)

## 🚧 Upcoming Features

- **Azure TTS Integration**: High-quality voice synthesis
- **Memory Search Commands**: "What did I tell you about..."
- **Enhanced GUI**: Better aesthetics and user experience
- **Voice Activation**: Wake word detection
- **Multi-modal**: Image and document processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **DeepSeek** for the excellent R1 reasoning model
- **Groq** for fast, reliable API access
- **Azure** for speech services integration
- **Community** for feedback and suggestions