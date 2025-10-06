from typing_extensions import TypedDict,List
from langgraph.graph.message import add_messages
from typing import Annotated
from pydantic import BaseModel, Field
from typing import Literal


# class State(TypedDict):
#     """ 
#         Represent the structure of state used in graph
#     """
#     messages:Annotated[List,add_messages]

class State(TypedDict, total=False):
    """
    Represent the structure of state used in graph.
    messages is optional (total=False) so graph compile/validation won't fail
    if no messages are present yet. The add_messages reducer will append messages.
    """
    messages: Annotated[List, add_messages]


#Router
class RouteQuery(BaseModel):
  """ Route a user query to the most relevant datasources"""

  datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
  )



  
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


### Hallucination Grader

class Hallicination(BaseModel):
  """ Binary score for hallucination present in generation answer."""
  binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
  )



# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


class GraphState(TypedDict):
  """ Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
  """
  question:str
  generation:str
  documents:List[str]