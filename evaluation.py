'''
This script purpose is to pass a list of test data through different models, and store their output
'''

import os
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

client = MistralClient(api_key=api_key)

entries = []
with open("test/test_pass.jsonl", 'r') as infile:
    for line in infile:
        try:
            entry = json.loads(line)
            entries.append(entry)
        except json.JSONDecodeError:
            print(f"Ignoring invalid JSON: {line}")

def gen_response(tuple, model):
    '''
    Generates a 200 explanation as for why the gene and cpd lists point to a certain metabolic pathway
    :param tuple: (gene, cpd) tuple
    :param model: string, model to use
    :return: string, text message
    '''
    gene, cpd = tuple
    gene_list = (',').join(gene)
    compound_list = (',').join(cpd)
    prompt_item = (f'List of genes : <<< {gene_list} >>>\nList of compounds : <<< {compound_list} >>>')
    messages = [
        ChatMessage(role="system", content="Find the altered pathway, <200 words."),
        ChatMessage(role="user", content=prompt_item),
        ]
    chat_response = client.chat(
        model=model,
        messages=messages
    )
    explanation = chat_response.choices[0].message.content
    print(f'{len(gene)} Genes and {len(cpd)} compounds. Assistant content : {explanation} char.')
    return explanation

def test_pass_model(entries, model):
    '''
    Call previous function to fill entries with specified model replies
    :param entries: list of dict (jsonl)
    :param model: string, model name
    :return:
    '''
    for entry in entries:
        gene = entry["input"]["genes"]
        cpd = entry["input"]["cpd"]
        rep = gen_response((gene, cpd), model)
        # entry["output"] = {}
        entry["output"][model] = rep
    return entries

model = 'mistral-small-latest'
test_res = test_pass_model(entries, model)
with open("test/test_pass5.jsonl", 'w') as outfile:
    for entry in test_res:
        json.dump(entry, outfile)
        outfile.write('\n')

# for model in client.list_models().data:
#     print(model.id)