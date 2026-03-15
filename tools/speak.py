#!/usr/bin/env python3
"""
Text-to-Speech tool using Windows Speech Synthesis - optimized for speed.
"""

import json
import subprocess
import sys


def speak_windows(text: str) -> bool:
    ps_script = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{text.replace('"', "'").replace(chr(92), chr(92)+chr(92))}")'
    try:
        subprocess.Popen(
            ['powershell', '-Command', ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False


def main() -> int:
    try:
        input_data = sys.stdin.read().strip()

        if not input_data:
            print(json.dumps({"success": False, "message": "No input provided."}))
            return 1

        data = json.loads(input_data)
        text = data.get("text", "").strip()

        if not text:
            print(json.dumps({"success": False, "message": "No text provided."}))
            return 1

        if not speak_windows(text):
            print(json.dumps({"success": False, "message": "Failed to speak."}))
            return 1

        print(json.dumps({"success": True, "message": "Speech played successfully."}))
        return 0

    except Exception as e:
        print(json.dumps({"success": False, "message": f"Error: {str(e)}"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
