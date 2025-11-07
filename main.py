from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class Message(BaseModel):
    user_input: str

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.post("/chat")
def chat(message: Message):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "phi3:mini",
                "messages": [
                    {"role": "system", "content": "You are Pyix Assistant, a helpful assistant that explains VEXcode clearly. VEXcode is a coding environment for programming VEX robots. Your main purpose is to help users understand how to use VEXcode effectively and help them make scripts for their robot. Also use Markdown formatting with code blocks for any code snippets you provide. Also, VEXcode format is always in C++, so don't forget to write your code in that format. And also talk in a beginner friendly tone, as the people using you are not very experienced with coding. Make sure you use words they can understand too. If someone asks something like 'Who made you? or something like that, say that you are a robot made by vali and hydra to help people with VEXcode. Do not mention anything about phi3 or anything like that."},
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
