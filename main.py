from langchain.memory import ConversationBufferMemory,ConversationBufferWindowMemory
from langchain import PromptTemplate
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
from langchain.embeddings import SentenceTransformerEmbeddings
from fastapi import FastAPI, Request, Form, Response,Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant
import os
import json
from datetime import datetime, timedelta 
# from textblob import TextBlob
from langchain.chains import ConversationChain
# from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
import csv
import datetime
import pytz
from langchain_community.llms import Ollama
import os
# from pymongo import MongoClient
# from bson.objectid import ObjectId
import json
# import mysql.connector
import re
import warnings
from typing import List
# import torch
from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.llms import HuggingFacePipeline
from langchain.schema import BaseOutputParser
from transformers import (AutoModelForCausalLM,AutoTokenizer,StoppingCriteria,StoppingCriteriaList,pipeline,AutoModelForSeq2SeqLM, BitsAndBytesConfig,)
from huggingface_hub import login
warnings.filterwarnings("ignore", category=UserWarning)
from langchain.agents import AgentType, initialize_agent
#from langchain.chat_models import ChatOpenAI
from transformers import StoppingCriteria
from transformers import StoppingCriteriaList
from langchain.llms import HuggingFacePipeline
from langchain.schema import BaseOutputParser
from transformers import pipeline
from transformers import BitsAndBytesConfig
from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer

from datetime import datetime
from langchain import PromptTemplate, LLMChain
from langchain.agents import Tool
from langchain.chains import LLMMathChain
# from langchain_nomic.embeddings import NomicEmbeddings
from deep_translator import GoogleTranslator,single_detection
import google.generativeai as palm
from langchain.embeddings import GooglePalmEmbeddings
from langchain.llms import GooglePalm
from langchain_google_genai import GoogleGenerativeAI









os.environ['GOOGLE_API_KEY'] =  'AIzaSyCjyyhW36eS4Tkk6N2gITsBDOR6Q9kJeRI'

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

print("LLM Initialized....")

embeddings = GooglePalmEmbeddings()

url = "http://localhost:6333"

client = QdrantClient(
    url=url, prefer_grpc=False
)

db = Qdrant(client=client, embeddings=embeddings, collection_name="vector_db")

retriever = db.as_retriever(search_kwargs={"k":3})


llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key="AIzaSyCjyyhW36eS4Tkk6N2gITsBDOR6Q9kJeRI", temperature=0.1)
# llm=Ollama(base_url="https://0fbf-34-93-152-221.ngrok-free.app",model="mistral")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    query_param1 = request.query_params.get('phone')
    print("parameter1",query_param1)
    query_param2 = request.query_params.get('timestamp')
    print("parameter2",query_param2)
    return templates.TemplateResponse("index.html", {"request": request, "phone": query_param1,"timestamp": query_param2})



prompt_template = """
    Use the following pieces of information to answer the user's question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    if the user asks something that is not present inside your knowledge base then say I don't know
    

    Context2:

    <hs>
    {history}
    </hs>
    """
context_message="""    Context: {context}
                           Question: {question}

                           Only return the short and helpful answer below and nothing else.
                           Helpful short and summarised answer :
     """



prompt_template=prompt_template+ context_message 
    
print(prompt_template)


prompt = PromptTemplate(template=prompt_template, input_variables=['history','context', 'question'])


qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type='stuff',
    retriever=retriever,
    verbose=True,
    chain_type_kwargs={
        "verbose": True,
        "prompt": prompt,
        "memory": ConversationBufferMemory(
            memory_key="history",
            input_key="question"
            ),
    }
    )
@app.post("/get_response")
async def get_response(query: str = Form(...),phoneNumber: str = Form(...),timestamp: str = Form(...),selectedLanguage: str = Form(...)):    
    global sql_response
    
    translator = GoogleTranslator(source=f'{selectedLanguage}', target='en')
    print(selectedLanguage)
    query=translator.translate(query)




    print("qa_chain",qa)

    response = qa(query)

    print(qa.combine_documents_chain.memory)

    print(response['result'])
    final_answer=response['result']
    translator = GoogleTranslator(source='en', target=f'{selectedLanguage}')
    final_answer=translator.translate(final_answer)
    response['result'] = f'{final_answer}'

    conversation = {
        "query": query,
        "result": response['result']
    }
    ticket={
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Chatbot Conversation": json.dumps(conversation)

    }

    csv_file_path = "Conversations/generated_responses.csv"
    with open(csv_file_path, mode='a', newline='') as file:        
        writer = csv.DictWriter(file, fieldnames=["Timestamp","Chatbot Conversation"])
        writer.writerow(ticket)

   
 
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000,debug=True)