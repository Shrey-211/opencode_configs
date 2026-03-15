#!/usr/bin/env python3
"""
Webhook server to invoke opencode tools remotely.
"""

import subprocess
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="OpenCode Webhook Server")

TOOLS_DIR = "C:/Users/Shrey/.config/opencode/tools"


class ToolRequest(BaseModel):
    tool: str
    params: Optional[Dict[str, Any]] = {}


@app.get("/")
async def root():
    return {"status": "online", "message": "OpenCode Webhook Server is running"}


@app.get("/tools")
async def list_tools():
    return {
        "available_tools": [
            "speak", "listen", "windows", "spotify"
        ]
    }


@app.post("/run/{tool_name}")
async def run_tool(tool_name: str, params: Optional[Dict[str, Any]] = None):
    if params is None:
        params = {}
    
    tool_map = {
        "speak": "speak.py",
        "listen": "listen.py",
        "windows": "windows.py",
        "spotify": "spotify.py",
    }
    
    if tool_name not in tool_map:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
    
    try:
        tool_file = tool_map[tool_name]
        
        if tool_name == "speak":
            if "text" not in params:
                raise HTTPException(status_code=400, detail="Missing required parameter: text")
            input_data = json.dumps({
                "text": params.get("text"),
                "voice": params.get("voice", "en-US-AriaNeural"),
                "rate": params.get("rate", "+0%"),
                "volume": params.get("volume", "+0%")
            })
        elif tool_name == "listen":
            input_data = json.dumps({
                "timeout": params.get("timeout", 10),
                "phrase_limit": params.get("phrase_limit", 5),
                "language": params.get("language", "en-US")
            })
        elif tool_name == "windows":
            input_data = json.dumps(params)
        elif tool_name == "spotify":
            input_data = json.dumps(params)
        else:
            input_data = json.dumps(params)
        
        result = subprocess.run(
            ["python", f"{TOOLS_DIR}/{tool_file}"],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        try:
            output = json.loads(result.stdout)
        except:
            output = {"raw_output": result.stdout, "stderr": result.stderr}
        
        return {
            "tool": tool_name,
            "params": params,
            "result": output,
            "success": result.returncode == 0
        }
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Tool execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speak")
async def speak(text: str, voice: str = "en-US-AriaNeural", rate: str = "+0%", volume: str = "+0%"):
    input_data = json.dumps({"text": text, "voice": voice, "rate": rate, "volume": volume})
    
    result = subprocess.run(
        ["python", f"{TOOLS_DIR}/speak.py"],
        input=input_data,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return {"success": result.returncode == 0, "output": result.stdout}


@app.post("/listen")
async def listen(body: Optional[Dict[str, Any]] = None):
    if body is None:
        body = {}
    timeout = body.get("timeout", 10)
    input_data = json.dumps({
        "timeout": timeout,
        "phrase_limit": body.get("phrase_limit", 5),
        "language": body.get("language", "en-US")
    })
    
    result = subprocess.run(
        ["python", f"{TOOLS_DIR}/listen.py"],
        input=input_data,
        capture_output=True,
        text=True,
        timeout=timeout + 10
    )
    
    try:
        output = json.loads(result.stdout)
    except:
        output = {"raw": result.stdout}
    
    return output


@app.post("/windows")
async def windows(body: Dict[str, Any]):
    action = body.get("action")
    if not action:
        raise HTTPException(status_code=400, detail="Missing required parameter: action")
    body["action"] = action
    input_data = json.dumps(body)
    
    result = subprocess.run(
        ["python", f"{TOOLS_DIR}/windows.py"],
        input=input_data,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    try:
        output = json.loads(result.stdout)
    except:
        output = {"raw": result.stdout}
    
    return output


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
