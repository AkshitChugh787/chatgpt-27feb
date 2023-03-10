# -*- coding: utf-8 -*-
"""VGPT_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ycRxjNaeWpRE7a0hIOFR3DtdNXBXRa2q
"""

#pip install langchain

#pip install openai

#pip install chromadb

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.elastic_vector_search import ElasticVectorSearch
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate

import os
os.environ['OPENAI_API_KEY'] = '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'

with open('text.txt') as f:
    state_of_the_union = f.read()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_text(state_of_the_union)

embeddings = OpenAIEmbeddings()

import chromadb
import pandas as pd
df=pd.read_csv('pat_data.csv')
df=df[:60]
df.drop(['Unnamed: 0','patientmasterkey','patientrecordkey'],axis=1,inplace=True)

class MyDocument:
    def __init__(self, text, metadata=None):
        self.text = text
        self.metadata = metadata
        self.page_content = text  # add this line to define page_content attribute
metadata = [{'source': str(i)} for i in range(len(texts))]
documents = [MyDocument(text, metadata=metadata[i]) for i, text in enumerate(texts)]
docsearch = Chroma.from_documents(documents, embeddings)

query = "What did the president say about Justice Breyer"
docs = docsearch.similarity_search(query,k=1)

from langchain.chains.question_answering import load_qa_chain
import openai
from langchain.llms import OpenAI

chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")
#query ='how many patient suffering from Opioid dependence ?'
def response_query(query):
  result=chain.run(input_documents=docs, question=query)
  # print(result.strip()=="I don't know.")
  if result.strip()=="I don't know.":
    print('query: ',query)
    #print(result)
    response = openai.Completion.create(
                  model='text-davinci-003',
                  prompt=query,
                  temperature=0.0,
                  max_tokens=60,
                  top_p=1,
                  frequency_penalty=0,
                  presence_penalty=0.6,
    )
    return(response.choices[0].text.strip())
  else:
    return(result)

#! pip install streamlit
import streamlit as st

import streamlit as st
from transformers import pipeline

# Load pre-trained NLP model


# Define Streamlit app
def app():
    st.header("VGPT")
    st.title('sample of dataset')
    st.write(df.head())
    st.write('This chatbot gives answer from our data as well as from chatgpt')
    st.write()
    st.write('Sometime we need to mention in what context user want to see the answer')
    st.write()
    st.write("If you don't get your expected response, please change the format of your question ")
    st.write()
    st.write("Model is trained on 60 records only so, it may be possible that user don't get expected responses from our dataset" )
    #chat_history = []
    input_placeholder = "Type your message here..."

    # Get user input
    query = st.text_input("User: ", "",placeholder=input_placeholder)

    if st.button("Send"):
        response=response_query(query)
        st.text_area("Bot:", value=response, height=50, max_chars=None)

#         chat_history.append(('User', query))
#         bot_response = response_query(query)
#         chat_history.append(('Bot', bot_response))
#         #st.write(response_query(query)
#     st.write("Chat History:")
#     for chat in chat_history:
#         st.write(f"{chat[0]}: {chat[1]}")

if __name__ == '__main__':
    app()

