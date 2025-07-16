# Companion AI v2.0

An advanced conversational AI companion with persistent memory, natural conversation flow, and evolving personality. Built with DeepSeek R1 for high-quality reasoning and contextual awareness.

## 🌟 Key Features

### 🧠 **Intelligent Memory System**
- **Persistent Memory**: Remembers conversations, preferences, and insights across sessions
- **Relevance-Based Retrieval**: Finds relevant memories based on conversation context, not just recent ones
- **Smart Storage**: Importance-weighted memory with automatic cleanup and deduplication
- **Contextual Awareness**: Uses memory subtly to inform responses without being pushy

### 💬 **Natural Conversation**
- **DeepSeek R1 Integration**: Advanced reasoning with transparent thinking process
- **Adaptive Personality**: Evolves naturally through interactions while maintaining core traits
- **Context-Aware Responses**: References past conversations only when appropriate
- **Human-like Flow**: Responds to what you're saying NOW, not forcing past topics

### 🖥️ **Modern Interface**
- **Clean GUI**: Modern tkinter interface with dark theme
- **Thinking Toggle**: Show/hide AI reasoning process
- **Real-time Processing**: Threaded responses for smooth interaction
- **Memory Insights**: View conversation statistics and stored memories

### 🎤 **Voice Capabilities** (Ready for Azure TTS)
- **Speech Recognition**: Convert speech to text
- **Audio Processing**: Smart microphone calibration and noise handling
- **Azure Integration**: Ready for high-quality text-to-speech

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
   # Modern GUI (Recommended)
   python gui_app.py
   
   # Alternative text interface
   python gui.py
   
   # Voice-enabled mode
   python main.py
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
│   └── __init__.py
├── data/                  # SQLite database storage
│   └── companion_ai.db    # Persistent memory database
├── gui_app.py            # Modern GUI (Recommended)
├── gui.py                # Alternative text interface
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