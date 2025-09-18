from src.langgraphagenticai.state.State import State


class ChatbotWithTool:
    def __init__(self,model):
        self.llm=model
    def create_chatbot(self,tools):
        """
        Returns a chatbot node function.
        """
        llm_with_tools=self.llm.bind_tools(tools)
        def chatbot_node(state : State):
            """
            Chatbot logic for processing the input state and returning a response.
            """
            return {"messages": [llm_with_tools.invoke(state["messages"])]}
        return chatbot_node

        


        