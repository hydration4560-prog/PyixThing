from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import json
import os
from pathlib import Path

app = FastAPI()

class Message(BaseModel):
    user_input: str

@app.get("/")
def home():
    path = Path(__file__).parent / "static" / "index.html"
    return FileResponse(path)

@app.post("/chat")
def chat(message: Message):
    try:
        ai_url = os.getenv("AI_URL", "http://localhost:11434/api/chat")
        response = requests.post(
            ai_url,
            json={
                "model": "phi3:mini",
                "messages": [
                    {
                        "role": "system", ## do not touch ANY of this since the bottom is secondary instructions and if you change anything it will break the ai's functionality since I tweaked a bunch of stuff in the API
                        "content": (
                            "You are Pyix Assistant, a helpful assistant that explains VEXcode clearly. "
                            "VEXcode is a coding environment for programming VEX robots. Your main purpose is to help users "
                            "understand how to use VEXcode effectively and help them make scripts for their robot. "
                            "Also use Markdown formatting with code blocks for any code snippets you provide. "
                            "Also, VEXcode format is always in C++, so don't forget to write your code in that format. "
                            "Talk in a beginner-friendly tone, as the people using you are not very experienced with coding. "
                            "If someone asks something like 'Who made you?', say that you are a robot made by Vali and Hydra "
                            "to help people with VEXcode."
                        )
                    },
                    {"role": "user", "content": message.user_input}
                ]
            },
            stream=True
        )

        full_text = ""
        for line in response.iter_lines():
            if line:
                try:
                    obj = json.loads(line.decode("utf-8").strip())
                    content = obj.get("message", {}).get("content")
                    if content:
                        full_text += content
                except Exception:
                    pass

        return {"response": "🤖 Pyix Assistant: " + (full_text if full_text else "No response from model.")}

    except Exception as e:
        return {"response": f"🤖 Pyix Assistant: Error contacting AI model: {str(e)}"}
