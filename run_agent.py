from src.app_agents.main_agent.agent import MainAgent
from src.infrastructure.repository import print_db


PROMPTS = [
    # "Ajoute un niveau Rez-de-chaussée avec floor_number 0.",
    # "Ajoute un espace Cuisine sur le niveau Rez-de-chaussée.",
    # "Renomme la Cuisine en Cuisine ouverte.",
    # "Ajoute une Chambre sur un niveau qui n'existe pas pour vérifier la gestion d'erreur.",
    "Create a three-story house with a basement and an attic. Add two rooms on each floor, and one room in the attic. Rename one of the rooms on the second floor. Add a reason why one of the rooms in the attic is not accessible for visiting.",
]

if __name__ == "__main__":
    agent = MainAgent()
    chat = agent.create_chat()

    for prompt in PROMPTS:
        print("USER:", prompt)
        print("AGENT:", agent.ask(prompt, chat))
        print()

    print_db()
