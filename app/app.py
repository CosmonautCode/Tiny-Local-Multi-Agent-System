
from app.llm.chat import ChatSystem




def main():
    chat = ChatSystem()
    chat.load_agents()
    chat.chat_loop()

if __name__ == "__main__":
    main()
