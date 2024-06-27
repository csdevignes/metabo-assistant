'''
This script purpose is to fine tune a mistral model with created dataset
'''

import os
import json
from mistralai.client import MistralClient
from mistralai.models.jobs import TrainingParameters
from mistralai.models.chat_completion import ChatMessage

# This part split the dataset into train and validation set
def split_jsonl(datafile, outf_train, outf_val):
    t_size = 430
    entries = []
    with open(datafile, 'r') as infile:
        for line in infile:
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError:
                print(f"Ignoring invalid JSON: {line}")
    with open(outf_train, 'w') as outfile:
        for entry in entries[:t_size]:
            json.dump(entry, outfile)
            outfile.write('\n')
    with open(outf_val, 'w') as outfile:
        for entry in entries[t_size:]:
            json.dump(entry, outfile)
            outfile.write('\n')

# split_jsonl("dataset/train_dataset_lab.jsonl", "train/7B_20240628/train.jsonl", "train/7B_20240628/val.jsonl" )

api_key = os.environ.get("MISTRAL_API_KEY")
client = MistralClient(api_key=api_key)

# with open("train/7B_20240628/train.jsonl", "rb") as f:
#     dbexamples_train = client.files.create(file=("dbexamples_train.jsonl", f))
# with open("train/7B_20240628/val.jsonl", "rb") as f:
#     dbexamples_eval = client.files.create(file=("dbexamples_eval.jsonl", f))
#
# print(dbexamples_train)
# print(dbexamples_eval)
#
created_jobs = client.jobs.create(
    model="open-mistral-7b",
    training_files=[dbexamples_train.id],
    validation_files=[dbexamples_eval.id],
    hyperparameters=TrainingParameters(
        training_steps=10,
        learning_rate=0.0001,
        )
)

# print(created_jobs)

retrieved_jobs = client.jobs.retrieve('e63dc09f-04a9-4678-acb7-b3b38bf8e7d2')

print(retrieved_jobs)

# chat_response = client.chat(
#     model='ft:open-mistral-7b:5aebfd1c:20240627:e63dc09f',
#     messages=[ChatMessage(role='user', content="List of genes : <<< PYGB,,HK1,GYS2,,GYS1,,G6PC2,MGAM2,ENPP3,AMY1A >>>\nList of compounds : <<< GDP-glucose,D-Glucose 6-phosphate,D-Glucose 6-phosphate >>>")]
# )
#
# print(chat_response.choices[0].message.content)