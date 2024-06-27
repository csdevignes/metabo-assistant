'''
This script purpose is to generate examples to use for training of the model
'''
import json
import random
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-small-latest"

client = MistralClient(api_key=api_key)

# Drawing of data to use for the exemple
def draw_gene_cpd(db, pathway):
    '''
    From a kegg pathway entry, draw a random list of genes and compounds involved, of varying length
    :param pathway:
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

def draw_example(db, keeper_pathways):
    '''
    Randomly pick a pathway entry from the kegg json file, and draw gene and cpd from it.
    Already highly represented while not very relevant pathways are excluded
    :return: (pathway, gene, cpd) tuple of lists
    '''
    pathway = 'hsa00524'
    while db[pathway]["name"] not in keeper_pathways:
        pathway = random.choice(list(db.keys()))
    name = db[pathway]["name"]
    gene, cpd = draw_gene_cpd(db, pathway)
    return (name, gene, cpd)

# Exemple generation from the data drawn
def gen_explanation(tuple, exprompt):
    '''
    Generates a 200 explanation as for why the gene and cpd lists point to a certain metabolic pathway
    :param tuple: (pathway, gene, cpd) tuple
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
    calls previous methods to make an exemple, and return the output as a json formatted file
    :param tuple: (pathway, gene, cpd) tuple
    :return: dict, json formatted
    '''
    pathway, gene, cpd = tuple
    gene_list = (',').join(gene)
    compound_list = (',').join(cpd)
    # For the no_context dataset, userprompt was removed.
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

with open('prompts/pathway_genes_compounds.json', 'r') as jsonfile:
    db = json.load(jsonfile)
with open('prompts/test_chat_prompt.txt', 'r') as f:
    metab_pathway_request = f.read()
with open('prompts/example_gen_prompt.txt', 'r') as f:
    explanation_request = f.read()

keeper_pathway = ['Phenylalanine metabolism', 'Sulfur metabolism',
       'Nicotinate and nicotinamide metabolism', 'Linoleic acid metabolism',
       'Purine metabolism', 'Glycerophospholipid metabolism',
       'Propanoate metabolism',
       'Ether lipid metabolism', 'Steroid biosynthesis',
       'Pentose and glucuronate interconversions', 'Fatty acid elongation',
       'Pantothenate and CoA biosynthesis', 'Fatty acid metabolism',
       'D-Amino acid metabolism', 'Folate biosynthesis',
       'Terpenoid backbone biosynthesis',
       'Amino sugar and nucleotide sugar metabolism',
       'Mucin type O-glycan biosynthesis', 'Sphingolipid metabolism',
       'Lipoic acid metabolism', 'Pyrimidine metabolism',
       'alpha-Linolenic acid metabolism', 'Nitrogen metabolism',
       'One carbon pool by folate',
       'Valine, leucine and isoleucine degradation']

with open('dataset/train_dataset_lab4.jsonl', 'w', encoding='utf-8') as f:
    for i in range(100):
        print(i)
        data_ex = draw_example(db, keeper_pathway)
        ex = make_example(data_ex, metab_pathway_request, explanation_request)
        json.dump(ex, f, ensure_ascii=False)
        f.write('\n')

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

# merge_jsonl('dataset/train_dataset_lab3.jsonl', 'dataset/train_dataset_lab4.jsonl',
#             'dataset/train_dataset_lab.jsonl')
