from typing_extensions import TypedDict,List
from langgraph.graph.message import add_messages
from typing import Annotated


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
