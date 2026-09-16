from src.app_agents.upgraded_agent.agent import UpgradedMainAgent
from src.infrastructure.repository import print_db
from enum import Enum


class Idees(Enum):
    # IDEA: <tuple>(question, <image_path:optional>)
    IDEA1_LIST_OF_ACTIONS: tuple = (
        "Ajoute un niveau Rez-de-chaussée avec floor_number 0. "
        "Ajoute un espace Cuisine sur le niveau Rez-de-chaussée. "
        "Renomme la Cuisine en Cuisine ouverte. "
        "Ajoute une Chambre sur un niveau qui n'existe pas pour vérifier la gestion d'erreur. "
    ),

    IDEA2_ABSTRACT_INSTRUCTION: tuple = (
        "Create a three-story house with a basement and an attic. Add two rooms on each floor, "
        "and one room in the attic. Rename one of the rooms on the second floor."
        "Add a reason why one of the rooms in the attic is not accessible for visiting.",
    ),

    IDEA3_IMAGE_INSTRUCTION: tuple = "Here is my house scheme on the image, fill it in db", "static/images/house.png"
    IDEA4_LAST_CONVERSATION: tuple = "During the last conversation we parsed my house. We need to add a garage",


if __name__ == "__main__":
    idea_to_test = Idees.IDEA4_LAST_CONVERSATION.value # CHANGE HERE TO TEST OTHER IDEAS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    agent = UpgradedMainAgent()
    chat = agent.create_chat()

    if len(idea_to_test) == 1:
        agent.ask(idea_to_test[0], chat=chat)
    else:
        agent.ask_with_image(*idea_to_test, chat=chat)

    print_db()
