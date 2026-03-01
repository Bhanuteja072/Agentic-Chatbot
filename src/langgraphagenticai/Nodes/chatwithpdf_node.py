from typing import List
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

from src.langgraphagenticai.tools.PDFtool import PDFTool
# from langchain_tavily import TavilySearch
from src.langgraphagenticai.state.State import GraphState
from src.langgraphagenticai.state.State import RouteQuery
from src.langgraphagenticai.state.State import GradeDocuments, HallucinationCheck, GradeAnswer
from src.langgraphagenticai.llms.groqllm import GroqLlm





def init_components(user_controls):
    """
        Initialize all LLM-dependent components after we have the API key
    """
    llm = GroqLlm(user_controls).get_llm_mode()
    if not llm:
        raise ValueError("GROQ LLM not initialized. Please check your API key/model.")
    
    structured_llm_router = llm.with_structured_output(RouteQuery)
    system = """
    You are an expert at routing a user question to a vectorstore or web search

    Rules:
    - If the user's question is about content you know is in our internal vectorstore return "vectorstore".
    - Otherwise, return "web_search".
    - If you are uncertain, return "web_search".
    """

    prompt=ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{question}")
    ])

    question_router = prompt | structured_llm_router

    structured_llm_grader = llm.with_structured_output(GradeDocuments)
    system = """You are a grader assessing relevance of a retrieved document to a user question. \n
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""


    grade_prompt=ChatPromptTemplate.from_messages(
        [
            ("system",system),
            ("human","Retrieved document: \n\n {document} \n\n User question: {question}")
        ]
    )

    retrieval_grader = grade_prompt | structured_llm_grader

    prompt = hub.pull("rlm/rag-prompt")

    # Post-processing
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    rag_chain = prompt | llm | StrOutputParser()

    structured_llm_grader = llm.with_structured_output(HallucinationCheck)

    # Prompt
    system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
        Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""


    hallicinnation_prompt=ChatPromptTemplate.from_messages(
        [
            ("system",system),
            ("human","Retrieved facts: \n\n {facts} \n\n LLM generation: {generation}")
        ]
    )


    hallucination_grader = hallicinnation_prompt | structured_llm_grader


    structured_llm_grader = llm.with_structured_output(GradeAnswer)

    # Prompt
    system = """You are a grader assessing whether an answer addresses / resolves a question \n
        Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
        ]
    )

    answer_grader = answer_prompt | structured_llm_grader

    system = """You a question re-writer that converts an input question to a better version that is optimized \n
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved and accurate question in a single line.",
            ),
        ]
    )


    question_rewriter = re_write_prompt | llm | StrOutputParser()

    return (question_router, retrieval_grader, rag_chain, hallucination_grader, answer_grader, question_rewriter)








    





# llm=ChatGroq(model="qwen/qwen3-32b")
# structured_llm_router = llm.with_structured_output(RouteQuery)


#prompt






# llm=ChatGroq(model="qwen/qwen3-32b")


# Prompt
# system = """You are a grader assessing relevance of a retrieved document to a user question. \n
#     If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
#     It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
#     Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""


# grade_prompt=ChatPromptTemplate.from_messages(
#     [
#         ("system",system),
#         ("human","Retrieved document: \n\n {document} \n\n User question: {question}")
#     ]
# )

# retrieval_grader = grade_prompt | structured_llm_grader




# llm=ChatGroq(model="qwen/qwen3-32b")
# Prompt
# prompt = hub.pull("rlm/rag-prompt")

# # Post-processing
# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)
# rag_chain = prompt | llm | StrOutputParser()




# llm=ChatGroq(model="qwen/qwen3-32b")
# structured_llm_grader = llm.with_structured_output(Hallicination)

# # Prompt
# system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
#      Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""


# hallicinnation_prompt=ChatPromptTemplate.from_messages(
#     [
#         ("system",system),
#         ("human","Retrieved facts: \n\n {facts} \n\n LLM generation: {generation}")
#     ]
# )


# hallucination_grader = hallicinnation_prompt | structured_llm_grader



# LLM with function call
# llm=ChatGroq(model="qwen/qwen3-32b")

# structured_llm_grader = llm.with_structured_output(GradeAnswer)

# # Prompt
# system = """You are a grader assessing whether an answer addresses / resolves a question \n
#      Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
# answer_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system),
#         ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
#     ]
# )

# answer_grader = answer_prompt | structured_llm_grader




# llm=ChatGroq(model="qwen/qwen3-32b")
# Prompt
# system = """You a question re-writer that converts an input question to a better version that is optimized \n
#      for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
# re_write_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system),
#         (
#             "human",
#             "Here is the initial question: \n\n {question} \n Formulate an improved and accurate question in a single line.",
#         ),
#     ]
# )


# question_rewriter = re_write_prompt | llm | StrOutputParser()



def retrieve(state : GraphState,retriever):
  """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
  """
  print("---RETRIEVE---")
  question=state["question"]
  if retriever is None:
    raise ValueError("Retriever is not initialized. Please re-upload the PDF.")

  docs=retriever.invoke(question)

  return {"documents":docs , "question":question}


#generate

def generate(state : GraphState ,rag_chain):
  """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
  """
  print("---GENERATE---")
  question=state["question"]
  docs=state["documents"]
  generation=rag_chain.invoke({"context":docs,"question":question})
  return {"documents": docs, "question": question, "generation": generation}



def grade_docs(state : GraphState ,retrieval_grader):
  """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
  """
  print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
  question=state["question"]
  docs=state["documents"]
  # Score each doc
  filtered_docs = []
  for d in docs:
      score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
      grade = score.binary_score
      if grade == "yes":
          print("---GRADE: DOCUMENT RELEVANT---")
          filtered_docs.append(d)
      else:
          print("---GRADE: DOCUMENT NOT RELEVANT---")
          continue
  return {"documents": filtered_docs, "question": question}










def transform_query(state : GraphState ,question_rewriter):
  """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
  """
  question=state["question"]
  documents = state["documents"]

  print("---TRANSFORM QUERY---")
  new_question=question_rewriter.invoke({"question":question})
  return {"documents": documents, "question": new_question}



# def websearch(state : GraphState , web_search_tool):
#   """
#     Web search based on the re-phrased question.

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): Updates documents key with appended web results
#   """
#   print("---WEB SEARCH---")
#   question = state["question"]
# #   web_search_tool = TavilySearch(k=3)
#   docs = web_search_tool.invoke({"query": question})
#   # print(docs)
#   results = docs.get("results", [])
#   web_results_text = "\n\n".join([r["content"] for r in results if r.get("content")])
#   web_results = Document(page_content=web_results_text)
#   return {"documents": web_results, "question": question}



def route_question(state : GraphState , question_router):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"
    

def decide_to_generate(state : GraphState):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"
    

def grade_generation_v_documents_and_question(state : GraphState ,hallucination_grader, answer_grader):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"facts": documents, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"
