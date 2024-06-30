import json
import random
import sys

import pandas as pd

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

def draw_example(db, pathway_vc, n_item):
    '''
    Randomly pick a pathway entry from the kegg json file, and draw gene and cpd from it.
    Value count (vc) for each pathway ensure the dataset is balanced.
    :param db: kegg database json with pathways, genes and compounds
    :param pathway_vc: dict containing the number of example already drawn per pathway
    :return: (pathway, gene, cpd) tuple of lists
    '''
    pathway = random.choice(list(db.keys()))
    item_per_pathway = n_item // len(db)
    if sum(pathway_vc.values()) < len(db)*item_per_pathway:
        while pathway_vc[pathway] >= item_per_pathway:
            pathway = random.choice(list(db.keys()))
    pathway_vc[pathway] = pathway_vc[pathway ] +1
    name = db[pathway]["name"]
    gene, cpd = draw_gene_cpd(db, pathway)
    return (name, gene, cpd, pathway_vc)

def create_pathway_valuecount():
    '''
    Create a pathway_vc.csv file containing the list of pathway codes and initial value counts (0)
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
    pvc.to_csv('test/pathway_vc.csv', index_label='pathway_code')

def make_test_item(tuple):
    '''
    calls previous methods to make an exemple, and return the output as a json formatted file
    :param tuple: (pathway, gene, cpd) tuple
    :return: dict, json formatted
    '''
    pathway, gene, cpd = tuple
    item = {}
    item["input"] = {"genes" : gene,
                     "cpd" : cpd}
    item["target"] = pathway
    print(f'{pathway} : {len(gene)} Genes and {len(cpd)} compounds.')
    return item

def main(n_item, destfile):
    with open('prompts/pathway_genes_compounds.json', 'r') as jsonfile:
        db = json.load(jsonfile)
    # If 'test/pathway_vc.csv' was not previously created, run this line
    # But if generating dataset in multiple batches, comment it
    create_pathway_valuecount()
    pathway_vc = pd.read_csv('test/pathway_vc.csv', index_col='pathway_code').to_dict()['count']

    with open(destfile, 'w', encoding='utf-8') as f:
        for i in range(n_item):
            print(i)
            name, gene, cpd, pathway_vc = draw_example(db, pathway_vc, n_item)
            data_ex = (name, gene, cpd)
            ex = make_test_item(data_ex)
            json.dump(ex, f, ensure_ascii=False)
            f.write('\n')

    df = pd.DataFrame.from_dict(pathway_vc, orient='index', columns=['count'])
    df = df.reset_index().rename(columns={'index': 'pathway_code'})
    df.to_csv('test/pathway_vc.csv', index=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python testitemgeneration.py <number of tems (integer)> <destination_file>\nPlease note that destination file will be overwritten.")
        sys.exit(1)

    n_ex = sys.argv[1]
    destfile = sys.argv[2]
    main(int(n_ex), destfile)