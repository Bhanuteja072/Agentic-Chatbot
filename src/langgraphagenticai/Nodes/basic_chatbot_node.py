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
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import trim_messages

# -------------------------
# In-memory store for sessions
# -------------------------
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


class BasicChatbotNode:
    """
    Basic Chatbot with Memory + Trimming.
    Keeps independent conversation history for each Streamlit session.
    """

    def __init__(self, model):
        self.llm = model

        # Trimmer: keep last 200 tokens (tune as needed)
        self.trimmer = trim_messages(
            max_tokens=200,
            strategy="last",
            token_counter=self.llm,
            include_system=True,
            allow_partial=False,
            start_on="human"
        )

        # System + placeholder prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant. Answer to the best of your ability."),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # Build chain: trim → prompt → LLM
        self.chain = (
            RunnablePassthrough.assign(messages=itemgetter("messages") | self.trimmer)
            | self.prompt
            | self.llm
        )

        # Wrap with message history
        self.with_history = RunnableWithMessageHistory(
            self.chain,
            get_session_history,
            input_messages_key="messages",
        )

    def process(self, state: State) -> dict:
        """
        Process input and generate a chatbot response with memory.
        """
        messages = state.get("messages", [])
        session_id = state.get("session_id", "default_session")  # ✅ now dynamic

        # Extract user message
        user_message = ""
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, tuple) and len(last_message) >= 2:
                user_message = last_message[1]
            elif hasattr(last_message, "content"):
                user_message = getattr(last_message, "content", "")
            else:
                user_message = str(last_message)

        input_payload = {"messages": [HumanMessage(content=user_message)]}

        reply = self.with_history.invoke(
            input_payload,
            config={"configurable": {"session_id": session_id}}
        )

        reply_text = reply.content if hasattr(reply, "content") else str(reply)
        return {"messages": [("assistant", reply_text)]}
