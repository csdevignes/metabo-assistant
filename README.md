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

I extracted from scientific publications examples where researcher deduced a metabolic pathway from list of altered
genes and compounds (= **real examples**).
I also extracted from KEGG and NCBI database the list of all metabolic pathways, and for each the list of genes and
compounds involved (see [kegg-dataextract](https://github.com/csdevignes/kegg-dataextract) repository)
(= **database examples**).

While working with the database I realized that some pathways had zero compounds, only genes. Since I was interested
in crossing compounds and genes information, I excluded these pathways:
* Other glycan degradation
* Various types of N-glycan biosynthesis
* Other types of O-glycan biosynthesis
* Glycosaminoglycan biosynthesis - keratan sulfate

## LLM role - application behavior

The idea is to fine-tune a simple LLM model with data from cell metabolism, and assess if it can, based on a given list
of genes and compound, make interesting and relevant suggestions of altered metabolic pathways.

### Test using chat mistral

I first ran some test with mistral chat models to optimize the prompt and better define my case.
I used the [promptgenerator.py](promptgenerator.py) script to generate prompt from different real examples and then
tested it with the different mistral models. Test results are listed in [test-chat-results.md](prompts/test_chat_results.md)

Both Mistral Large and Small performed quite well, although they sometimes lacked precision and small model once did not
find the answer. Fine-tuning the small or 7B model with data from examples can maybe make it more precise
and accurate.

## Train dataset

Because of the lack of time, I could not mine the literature for sufficient real examples to have a train dataset.
I decided to generate examples from KEGG database data ([pathway_genes_compounds.json](prompts/pathway_genes_compounds.json)).
This was performed using [examplegeneration.py](examplegeneration.py)
Sets of (pathway, genes, compounds) were randomly drawn from KEGG database, and used to generate an explanation prompt
as for why this pathway is associated with these genes and compounds. I used mistral small since the chat test results
were OK. This explanation is then added to the dataset jsonl file, together with the userprompt containing genes
and compounds, without the pathway.

Part of the dataset (200 samples) is labelled with the pathway used to generate the examples, for verification purpose.
The label is then deleted to form final train dataset.

### Train dataset verifications

Performed in Jupyter notebook :
* pathway mentioned in assistant response is the right one (use of labelled dataset)
* representation of each pathway
* vagueness of the answer / useless sentences : hypotheses to filter out (as a future plan)
  * use another LLM to evaluate them
  * use embedding


