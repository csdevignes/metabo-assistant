'''
This script purpose is to pass a list of test data through different models, and store their output
'''

import os
import json
import sys

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = MistralClient(api_key=api_key)

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
    print(f'{len(gene)} Genes and {len(cpd)} compounds. Assistant {model} content : {len(explanation)} char.')
    return explanation

def item_pass_models(entry, model_list):
    '''
    Call previous function to fill entries with specified model replies
    :param entry: dict (json)
    :param model_list: list of string, model names
    :return:
    '''
    gene = entry["input"]["genes"]
    cpd = entry["input"]["cpd"]
    entry["output"] = {}
    for model in model_list:
        rep = gen_response((gene, cpd), model)
        entry["output"][model] = rep
    return entry

def main(test_items_file, outfile):
    entries = []
    with open(test_items_file, 'r') as infile:
        for line in infile:
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError:
                print(f"Ignoring invalid JSON: {line}")

    model_list = ['open-mistral-7b', 'mistral-small-latest']
    client_model_list = client.list_models()
    for item in client_model_list.data:
        if item.id.startswith('ft'):
            model_list.append(item.id)

    with open(outfile, 'w') as outfile:
        for entry in entries:
            res = item_pass_models(entry, model_list)
            json.dump(res, outfile)
            outfile.write('\n')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python evaluation.py <test item file> <destination_file>\nPlease note that destination file will be overwritten.")
        sys.exit(1)

    infile = sys.argv[1]
    outfile = sys.argv[2]
    main(infile, outfile)