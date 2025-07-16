# test_all_systems.py
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Initialize environment
load_dotenv()

# Import components
from companion_ai.llm_interface import generate_response, generate_groq_response
from companion_ai.memory import init_db, upsert_profile_fact, add_summary, add_insight, get_all_profile_facts

def test_groq():
    print("\n=== TESTING GROQ ===")
    response = generate_groq_response("Hello, this is a Groq test!")
    print(f"Groq Response: {response}")



def test_memory():
    print("\n=== TESTING MEMORY ===")
    # Add test data
    upsert_profile_fact("test_key", "test_value")
    add_summary("This is a test summary")
    add_insight("This is a test insight")
    
    # Retrieve data
    print("Profile Facts:", get_all_profile_facts())
    
def test_tts():
    print("\n=== TESTING TTS ===")
    # We'll need to mock the player for this test
    class MockPlayer:
        def play_chunk(self, chunk):
            print(f"Received audio chunk: {len(chunk)} bytes")
    
    from main import speak_text_azure_stream
    speak_text_azure_stream("This is a TTS test", MockPlayer())

def test_full_flow():
    print("\n=== TESTING FULL FLOW ===")
    memory_context = {
        "profile": get_all_profile_facts(),
        "summaries": [],
        "insights": []
    }
    response = generate_response("Hello, this is a full system test!", memory_context)
    print(f"System Response: {response}")

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Run tests
    test_groq()
    test_memory()
    test_tts()
    test_full_flow()
    
    print("\nAll tests completed!")