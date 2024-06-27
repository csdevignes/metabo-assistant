# metabo-assistant

This project was developed for the Mistral AI fine-tuning Hackathon, taking place in June 2024.

## Scientific background

Inside the cells, metabolic pathways are what determine is sugar is going to be converted to energy or fat for example.
They are composed of genes which can be more or less expressed (meaning there are more or less enzymes produced from
these genes). Gene-derived enzymes convert compounds (for example sugar) into another (for example fat).

Metabolic pathways are often altered in many diseases. To study these pathways in an exploratory way, researchers rely
on the measurements of gene expression and compound amounts. This will lead to having a list of genes, and a list of
compound, and wanting to deduce from these the metabolic pathway that is involved (called candidate pathway).

### Metabolic data collection

I extracted from the scientific publications examples where researcher deduced a metabolic pathway from list of altered
genes and compounds (= real examples).
I also extracted from KEGG and NCBI database the list of all metabolic pathways, and for each the list of genes and
compounds involved (see [kegg-dataextract](https://github.com/csdevignes/kegg-dataextract)
repository) (= database examples).

## LLM role - application behavior

The idea is to fine-tune a simple LLM model with data from cell metabolism, and assess if it can, based on a given list
of genes and compound, find interesting suggestions of altered metabolic pathways.

### Test using chat mistral

I first ran some test with mistral chat models to optimize the prompt and better define my case.
I used the promptgenerator.py script to generate prompt from different real examples and then tested it with the
different mistral models. Test results are listed in test-chat-results.md

Both Mistral Large and Small perform quite OK, although they sometimes lack precision and small did not found the answer
for one of the example. Fine-tuning the small model with precise data from examples can maybe make it more precise
and accurate.

## Train dataset

Because of the lack of time, I could not mine the litterature for sufficient real example to have a train dataset.
I decided to generate examples from KEGG database extracted data. These data are kept in pathway_genes_compounds.json


