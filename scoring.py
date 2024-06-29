'''
This script purpose is to have a LLM evaluate the answers of other LLM
'''

import os
import json, yaml
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

client = MistralClient(api_key=api_key)

def gen_eval_prompt(line, eval_prompt, metrics):
    '''
    Generates a 200 explanation as for why the gene and cpd lists point to a certain metabolic pathway
    :param tuple: (gene, cpd) tuple
    :param model: string, model to use
    :return: string, text message
    '''
    gene = line['input']['genes']
    cpd = line['input']['cpd']
    target = line['target']
    output = line["output"]
    gene_list = (',').join(gene)
    compound_list = (',').join(cpd)
    prompt = (f'{eval_prompt}\n{metrics}\n# Inputs :\nGenes : "{gene_list}"\nCompounds : "{compound_list}"\n# Target : {target}\n# Output\n')
    for i, model in enumerate(output):
        prompt = prompt + f'## Ouput from LLM {i+1} : {model} : "{output[model]}"\n'
    return prompt

def evaluate_line(prompt):
    model = 'mistral-large-latest'
    chat_response = client.chat(
        model=model,
        messages=[ChatMessage(role="user", content=prompt)],
        response_format={"type": "json_object"}
    )
    eval = chat_response.choices[0].message.content
    return eval

entries = []
with open("test/test_pass.jsonl", 'r') as infile:
    for line in infile:
        try:
            entry = json.loads(line)
            entries.append(entry)
        except json.JSONDecodeError:
            print(f"Ignoring invalid JSON: {line}")

with open("test/metrics.yaml", 'r') as mf:
    metrics = yaml.safe_load(mf)

with open('prompts/evaluation_prompt.txt', 'r') as f:
    eval_prompt = f.read()

for model in client.list_models().data:
    if model.id.startswith('ft'):
        print(model)

print('\n Jobs')
for job in client.jobs.list().data:
    print(job)

with open("test/test_eval2.jsonl", 'w') as outfile:
    for entry in entries[0:2]:
        prompt = gen_eval_prompt(entry, eval_prompt, metrics)
        #eval = evaluate_line(prompt)
        # outfile.write(eval)
        # outfile.write('\n')

