'''
Streamlit app to chat with the models
'''

import streamlit as st
import os
from dotenv import load_dotenv, dotenv_values
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = MistralClient(api_key=api_key)

def load_model_list(client):
    model_list = ['open-mistral-7b', 'mistral-small-latest', 'mistral-large-latest']
    client_model_list = client.list_models()
    for item in client_model_list.data:
        if item.id.startswith('ft'):
            model_list.append(item.id)
    return model_list

def get_model_answer(model, list_genes, list_compounds):
    user_content = f'List of genes : <<< {list_genes} >>>\nList of compounds : <<< {list_compounds} >>>'
    messages = [
        ChatMessage(role="system", content="Find the altered pathway, <200 words."),
        ChatMessage(role="user", content=user_content)
        ]
    chat_response = client.chat(
        model=model,
        messages=messages,
    )
    return chat_response.choices[0].message.content


if 'model_list' not in st.session_state:
    st.session_state['model_list'] = load_model_list(client)

st.markdown(""" # Select from the different models :

Mistral models :
* open-mistral-7b
* mistral-small-latest
* mistral-large-latest

Models fine-tuned to deduce metabolism pathways:

* ft:open-mistral-7b:5aebfd1c:20240627:e63dc09f
(ending with f - first model trained on 500 exemples)
* ft:open-mistral-7b:5aebfd1c:20240628:de14ae4a
(ending with a - second model trained on 1000 exemples)
""")

st.selectbox("Model", st.session_state['model_list'], key='model_selection')

st.markdown("""Input list of altered genes and/or list of altered metabolic pathways (any separator)""")

with st.form("Request"):
    list_genes = st.text_input("List of genes", key="list_genes")
    list_compounds = st.text_input("List of compounds", key="list_compounds")
    submitted = st.form_submit_button("Send")
    if submitted:
        model = st.session_state["model_selection"]
        answer = get_model_answer(model, list_genes, list_compounds)
        st.session_state['last_answer'] = answer

if "last_answer" in st.session_state:
    st.write(st.session_state["last_answer"])