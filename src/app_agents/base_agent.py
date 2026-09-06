import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool


load_dotenv()


class BaseAgent:
    SYSTEM_PROMPT = ""
    model_name: str
    token: str

    def __init__(self, tools: list | None = None):
        self.tools = tools or []

        if self.model_name.lower().startswith(("gemini", "gemma")):
            self.model_name = "gpt-4o-mini"

        if not self.token:
            raise ValueError("CHAT_GPT_KEY is required")

        os.environ["OPENAI_API_KEY"] = self.token

        self.agent = Agent(
            name=self.__class__.__name__,
            instructions=self.SYSTEM_PROMPT,
            model=self.model_name,
            tools=[function_tool(tool) for tool in self.tools],
        )

    def create_chat(self) -> list[str]:
        return []

    def ask(self, question: str, chat: list[str] | None = None, config: dict | None = None) -> str | None:
        if chat is None:
            prompt = question
        else:
            chat.append("USER: " + question)
            prompt = "\n".join(chat)

        result = asyncio.run(Runner.run(self.agent, prompt))
        answer = result.final_output

        if isinstance(answer, str):
            if chat is not None:
                chat.append("AGENT: " + answer)
            return answer.strip()

        return str(answer) if answer is not None else None
