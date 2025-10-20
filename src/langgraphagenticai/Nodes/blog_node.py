from src.langgraphagenticai.state.blog_state import BlogState
from langchain_core.messages import SystemMessage, HumanMessage
class BlogNode:
    def __init__(self, llm):
        self.llm = llm

    def generate_blog_title(self, state: BlogState):
        """
        Generate a blog title based on the topic
        """

        if "topic" in state and state["topic"]:
            prompt="""
                   You are an expert blog content writer. Use Markdown formatting. Generate
                   a blog title for the {topic}. This title should be creative and SEO friendly

                   """
            system_msg = prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_msg)

            return {"blog" : {"title" : response.content}}
        
    def generate_blog_content(self,state : BlogState):
        if "topic" in state and state["topic"]:
            system_prompt = """You are expert blog writer. Use Markdown formatting.
            Generate a detailed blog content with detailed breakdown for the {topic}"""
            system_message = system_prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_message)
            return {"blog" : {"title" : state['blog']['title'], "content" : response.content}}
        

    def translation(self,state:BlogState):
        """
        Translate the content to the specified language.
        """
        translation_prompt="""
        Translate the following content into {current_language}.
        - Maintain the original tone, style, and formatting.
        - Adapt cultural references and idioms to be appropriate for {current_language}.

        ORIGINAL CONTENT:
        {blog_content}

        """
        blog_content = state["blog"]["content"]
        msg=[
            HumanMessage(translation_prompt.format(current_language=state["current_language"], blog_content=blog_content))

        ]
        translation_response = self.llm.invoke(msg)
        # ensure we return text content (consistent with other nodes)
        translated_text = getattr(translation_response, "content", translation_response)
        return {"blog" : {"content" : translated_text}}
    

    def route(self,state:BlogState):
        return {"current_language": state["current_language"]}
    

    def route_decision(self,state:BlogState):
        """
          Route the content to the respective translation function.
        """
        if state["current_language"] == "hindi":
            return "hindi"
        elif state["current_language"] == "french": 
            return "french"
        else:
            return state["current_language"]


