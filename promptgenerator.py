'''
This file purpose is to generate prompts to use in mistral chat
'''

import pandas as pd
import openpyxl

def get_example(paper_name, condition_name):
    df_pat = pd.read_excel("prompts/LittData.xlsx", f"{paper_name}_pathways")
    pathway = df_pat.loc[df_pat['Condition'] == condition_name, "Pathway"].tolist()
    pathway = ','.join(pathway)
    df_gene = pd.read_excel("prompts/LittData.xlsx", f"{paper_name}_genes")
    gene = df_gene.loc[df_gene['Condition'] == condition_name, "Gene"].tolist()
    gene = ','.join(gene)
    df_cpd = pd.read_excel("prompts/LittData.xlsx", f"{paper_name}_metab")
    cpd = df_cpd.loc[df_cpd['Condition'] == condition_name, 'Metabolite'].tolist()
    cpd = ','.join(cpd)
    return (pathway, gene, cpd)

with open('prompts/test_chat_prompt.txt', 'r') as f:
    metab_pathway_request = f.read()

paper_name = "SMF"
# paper_name = "Whitburn"
condition_name = "3D spheroids + palmitate vs 2D culture"
# condition_name = "Co-culture with Bone Marrow Stromal Cells vs. Monoculture"

pathway, gene_list, compound_list = get_example(paper_name, condition_name)
prompt = f'{metab_pathway_request}\nList of genes : <<< {gene_list} >>>\nList of compounds : <<< {compound_list} >>>'

print(prompt)
print(f'\n\nPathway was {pathway}')