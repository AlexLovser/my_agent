import asyncio
import os
from agents import Agent, Runner, function_tool
import base64
from pathlib import Path

def encode_image(path: str) -> str:
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode("utf-8")

class BaseAgent:
    SYSTEM_PROMPT = ""
    model_name: str
    token: str

    def __init__(self, tools: list | None = None):
        self.tools = tools or []

        if self.model_name.lower().startswith(("gemini", "gemma")):
            self.model_name = "gpt-4o-mini"

        if not self.token:
            raise ValueError("OPENAI_API_KEY is required")

        os.environ["OPENAI_API_KEY"] = self.token

        self.agent = Agent(
            name=self.__class__.__name__,
            instructions=self.SYSTEM_PROMPT,
            model=self.model_name,
            tools=[function_tool(tool) for tool in self.tools],
        )

    def preprare_input_data(self, file_path: str) -> str:
        # jpeg/png/webp/gif — обычно ок
        return f"data:image/jpeg;base64,{encode_image(file_path)}"

    def create_chat(self) -> list[str]:
        return []

    def ask_with_image(self, text: str, image_path: str, chat: list | None = None) -> str:
        image_url = self.preprare_input_data(image_path)

        user_message = {
            "role": "user",
            "content": [
                {"type": "input_text", "text": text},
                {"type": "input_image", "image_url": image_url},
            ],
        }

        if chat is None:
            messages = [user_message]
        else:
            chat.append(user_message)
            messages = chat

        result = asyncio.run(Runner.run(self.agent, input=messages))
        answer = result.final_output

        if chat is not None:
            chat.append({"role": "assistant", "content": answer})

        return answer
