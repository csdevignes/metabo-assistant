'''
This script purpose is to generate examples to use for training of the model
'''
import json
import random
import sys

import pandas as pd
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-small-latest"

client = MistralClient(api_key=api_key)

# Random drawing of data to use for the exemple
def draw_gene_cpd(db, pathway):
    '''
    From a kegg pathway entry, draw a random list of genes and compounds involved, of varying length
    :param db: dict from the json file containing kegg database information
    :param pathway: string, pathway code
    :return: (gene, cpd) tuple of lists
    '''
    p_genes = db[pathway]['genes']
    limit = min(25, len(p_genes))
    n_genes = random.randint(2, limit)
    gene = random.sample(p_genes, n_genes)
    p_cpd = db[pathway]['compounds']
    limit = min(25, len(p_cpd))
    n_cpd = random.randint(2, limit)
    cpd = random.sample(p_cpd, n_cpd)
    return (gene, cpd)

def draw_example(db, pathway_vc):
    '''
    Randomly pick a pathway entry from the kegg json file, and draw gene and cpd from it.
    Condition ensure that the program draw until all pathways have 11 examples.
    :param db: dict, kegg database json with pathways, genes and compounds
    :param pathway_vc: dict containing the number of example already drawn per pathway
    :return: (pathway, gene, cpd, pathway_vc) where pathway is a string, and gene and cpd are lists
    '''
    pathway = random.choice(list(db.keys()))
    if sum(pathway_vc.values()) < 968:
        while pathway_vc[pathway] >= 11:
            pathway = random.choice(list(db.keys()))
    pathway_vc[pathway] = pathway_vc[pathway]+1
    name = db[pathway]["name"]
    gene, cpd = draw_gene_cpd(db, pathway)
    return (name, gene, cpd, pathway_vc)

# Exemple generation from the data drawn
def gen_explanation(tuple, exprompt):
    '''
    Generates a 200 word explanation as for why the gene and cpd lists refer to a certain metabolic pathway
    :param tuple: (pathway, gene, cpd) tuple
    :param exprompt: string, instructions to generate the example explanation
    :return: string, text message
    '''
    pathway, gene, cpd = tuple
    gene_list = (',').join(gene)
    compound_list = (',').join(cpd)
    prompt_exgen = (f'{exprompt}\nList of genes : <<< {gene_list} >>>\nList of compounds : <<< {compound_list} >>>\n'
        f'Metabolic pathway : <<< {pathway} >>>')
    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="user", content=prompt_exgen)]
    )
    explanation = chat_response.choices[0].message.content
    return explanation

def make_example(tuple, userprompt, exprompt):
    '''
    calls previous methods to make an exemple, and return the output as a json formatted dict
    :param tuple: (pathway, gene, cpd) tuple
    :return: dict, json format
    '''
    pathway, gene, cpd = tuple
    gene_list = (',').join(gene)
    compound_list = (',').join(cpd)
    user_content = f'List of genes : <<< {gene_list} >>>\nList of compounds : <<< {compound_list} >>>'
    assistant_content = gen_explanation(tuple, exprompt)
    example = {}
    example["messages"] = []
    example["messages"].append({"role" : "user",
                              "content" : user_content})
    example["messages"].append({"role" : "assistant",
                              "content" : assistant_content})
    example["target"] = pathway
    print(f'{pathway} : {len(gene)} Genes and {len(cpd)} compounds. Assistant content : {len(assistant_content)} char.')
    return example
def create_pathway_valuecount():
    '''
    Initialize a pathway_vc.csv file containing the list of pathway codes and initial value counts (0)
    '''
    keggdf = pd.read_json('prompts/pathway_genes_compounds.json', orient='index')
    vc = {}
    pvc = {}
    for i in keggdf.index:
        name = keggdf.loc[i, 'name']
        if name in vc :
            pvc[i] = vc[name]
        else :
            pvc[i] = 0
    pvc = pd.DataFrame.from_dict(pvc, orient='index', columns=['count'])
    pvc.to_csv('dataset/pathway_vc.csv', index_label='pathway_code')

def main(n_examples, destfile):
    with open('prompts/pathway_genes_compounds.json', 'r') as jsonfile:
        db = json.load(jsonfile)
    with open('prompts/test_chat_prompt.txt', 'r') as f:
        metab_pathway_request = f.read()
    with open('prompts/example_gen_prompt.txt', 'r') as f:
        explanation_request = f.read()
    # If 'dataset/pathway_vc.csv' was not previously created, run this line
    # But if generating dataset in multiple batches, comment it
    create_pathway_valuecount()
    pathway_vc = pd.read_csv('dataset/pathway_vc.csv', index_col='pathway_code').to_dict()['count']

    with open(destfile, 'w', encoding='utf-8') as f:
        for i in range(n_examples):
            print(i)
            name, gene, cpd, pathway_vc = draw_example(db, pathway_vc)
            data_ex = (name, gene, cpd)
            ex = make_example(data_ex, metab_pathway_request, explanation_request)
            json.dump(ex, f, ensure_ascii=False)
            f.write('\n')

    df = pd.DataFrame.from_dict(pathway_vc, orient='index', columns=['count'])
    df = df.reset_index().rename(columns={'index': 'pathway_code'})
    df.to_csv('pathway_vc.csv', index=False)

# Code for merging jsonl in case of multiple generation attempt
def merge_jsonl(file1, file2, outfile):
    with open(outfile, 'w') as outfile:
        for fichier in [file1, file2]:
            with open(fichier, 'r') as infile:
                for line in infile:
                    try:
                        json.loads(line)
                        outfile.write(line)
                    except json.JSONDecodeError:
                        print(f"Invalid line : {line}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python examplegeneration.py <number of examples (integer)> <destination_file>\nPlease note that destination file will be overwritten.")
        sys.exit(1)

    n_ex = sys.argv[1]
    destfile = sys.argv[2]
    main(int(n_ex), destfile)

