from src.app_agents.image_agent.agent import ImageAgent
from src.infrastructure.repository import print_db


if __name__ == "__main__":
    agent = ImageAgent()

    chat = agent.create_chat()
    agent.ask_with_image(
        "Вот схемма моего дома, заполни ее в базу данных",
        "static/house.png",
        chat
    )

    print_db()
