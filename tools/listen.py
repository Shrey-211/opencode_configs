#!/usr/bin/env python3
"""
Speech-to-Text tool using Google Speech Recognition.
"""

import json
import sys
import speech_recognition as sr


def listen(timeout: int = 10, phrase_limit: int = 5, language: str = "en-US") -> dict:
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = recognizer.recognize_google(audio, language=language)
            return {"success": True, "text": text, "language": language}
    
    except sr.WaitTimeoutError:
        return {"success": False, "error": "timeout", "message": "No speech detected within timeout"}
    except sr.UnknownValueError:
        return {"success": False, "error": "unclear", "message": "Speech was unclear"}
    except sr.RequestError as e:
        return {"success": False, "error": "api_error", "message": f"API error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": "error", "message": str(e)}


def main() -> int:
    try:
        input_data = sys.stdin.read().strip()
        
        if not input_data:
            result = listen()
            print(json.dumps(result))
            return 0
        
        data = json.loads(input_data)
        
        timeout = data.get("timeout", 10)
        phrase_limit = data.get("phrase_limit", 5)
        language = data.get("language", "en-US")
        
        result = listen(timeout=timeout, phrase_limit=phrase_limit, language=language)
        print(json.dumps(result))
        return 0
    
    except json.JSONDecodeError:
        result = listen()
        print(json.dumps(result))
        return 0
    
    except Exception as e:
        print(json.dumps({"success": False, "error": "error", "message": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
