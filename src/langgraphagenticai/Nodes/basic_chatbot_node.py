# from src.langgraphagenticai.state.State import State
# class BasicChatbotNode:
#     """
#     Basic Chatbot login implementation
#     """
#     def __init__(self,model):
#         self.llm=model
#     def process(self,state:State) -> dict:
#         """
#         Processes the input state and generates a chatbot response.
#         """
#         user_message = state["messages"][-1][1]
#         reply = self.llm.invoke(user_message)
#         return {"messages": [("assistant", reply.content if hasattr(reply, "content") else str(reply))]}

        

from src.langgraphagenticai.state.State import State
from langchain.schema import HumanMessage, AIMessage

class BasicChatbotNode:
    """
    Basic Chatbot login implementation
    """
    def __init__(self,model):
        self.llm=model
    def process(self,state:State) -> dict:
        # """
        # Processes the input state and generates a chatbot response.
        # """
        """
        Processes the input state and generates a chatbot response.
        Always returns {"messages": [("assistant", "<text>")]}.
        """
        messages = state.get("messages", [])  # may be [] or a list of tuples/message objects
        user_message = ""
        if messages:
            last_message = messages[-1]
            # If tuple like ("user", "Hello")
            if isinstance(last_message, tuple) and len(last_message) >= 2:
                user_message = last_message[1]
            # If it's a LangChain message object with .content
            elif hasattr(last_message, "content"):
                user_message = getattr(last_message, "content", "")
            else:
                user_message = str(last_message)

        reply = self.llm.invoke(user_message)
                # Normalize reply to plain text
        if hasattr(reply, "content"):
            reply_text = reply.content
        elif isinstance(reply, dict) and "content" in reply:
            reply_text = reply["content"]
        else:
            reply_text = str(reply)

        return {
            "messages": [("assistant", reply_text)]  # this works if add_messages is applied
        }


        