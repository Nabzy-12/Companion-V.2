#!/usr/bin/env python3
"""
Simple Azure TTS test script to diagnose connection issues
"""

import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Force reload environment variables
load_dotenv(override=True)

def test_azure_tts():
    """Test Azure TTS connection and configuration"""
    
    # Get credentials
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")
    
    print(f"Testing Azure TTS...")
    print(f"Region: {speech_region}")
    print(f"Key length: {len(speech_key) if speech_key else 0} characters")
    print(f"Key starts with: {speech_key[:10] if speech_key else 'None'}...")
    
    if not speech_key or not speech_region:
        print("❌ Missing Azure credentials in .env file")
        return False
    
    try:
        # Create speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, 
            region=speech_region
        )
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
        
        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        print("🔄 Testing TTS synthesis...")
        
        # Test synthesis
        test_text = "Hello! This is a test of Azure Text-to-Speech."
        result = synthesizer.speak_text_async(test_text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("✅ TTS test successful!")
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            print(f"❌ TTS failed - Reason: {cancellation.reason}")
            if cancellation.error_details:
                print(f"❌ Error details: {cancellation.error_details}")
            return False
        else:
            print(f"❌ TTS failed - Result: {result.reason}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

if __name__ == "__main__":
    test_azure_tts()