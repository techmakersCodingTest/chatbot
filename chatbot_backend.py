from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import boto3

# Initialize model and retriever
model = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs=dict(temperature=0),
)

retriever = AmazonKnowledgeBasesRetriever(
    knowledge_base_id="GFUUIVUW6A",
    retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
)

system_prompt = (
    "Use the given context to answer the question. "
    "Instead of saying the given information, please always refer to the information as inventory. "
    "If you don't know the answer, say you don't know. "
    "Use three sentences maximum and keep the answer concise. "
    "Context: {context}\n"
    "Chat History: {chat_history}"
)

def get_chat_history_string(messages):
    return "\n".join(
        [f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}" for m in messages]
    )

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(model, prompt)
chain = create_retrieval_chain(retriever, question_answer_chain)

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

class CustomRunnableWithMessageHistory(RunnableWithMessageHistory):
    def invoke(self, inputs, config=None):
        session_id = config["configurable"]["session_id"]
        history = get_session_history(session_id)
        chat_history_str = get_chat_history_string(history.messages)
        inputs["chat_history"] = chat_history_str
        response = super().invoke(inputs, config)
        return response

conversational_rag_chain = CustomRunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

def demo_conversation(input_text: str, memory) -> str:
    session_id = memory["session_id"]
    history = get_session_history(session_id)
    history.add_user_message(input_text)
    
    response = conversational_rag_chain.invoke(
        {"input": input_text},
        config={"configurable": {"session_id": session_id}}
    )["answer"]
    
    history.add_ai_message(response)
    
    return response

def demo_memory():
    return {"session_id": "example_session_id"}

def sync():
    bedrock = boto3.client(service_name='bedrock-agent')
    response = bedrock.start_ingestion_job(dataSourceId='8JLQAXINJQ',
                                        knowledgeBaseId='GFUUIVUW6A')
    response_body = response.get('ingestionJob')
    print(response_body)