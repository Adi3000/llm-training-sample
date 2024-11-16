import json
import accelerate
import os
import sys
from accelerate import Accelerator
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, PreTrainedTokenizer, BitsAndBytesConfig
from peft import LoraConfig
_labels = {}

dataset_path = "./data/storyteller_dataset.d"
input_json_dataset = "./data/dataset.json"
hf_model = "leafspark/Llama-3.1-8B-MultiReflection-Instruct"

def tokenize(data):
    result = tokenizer(data['text'], padding="max_length", truncation=True, max_length=512)
    return {
        "input_ids": result["input_ids"][:-1],
        "attention_mask": result["attention_mask"][:-1],
    }

def build_train_data(json_file: str, tokenizer: PreTrainedTokenizer):
    with open(json_file, 'r') as f:
        data = json.load(f)
    train_data = []
    for quest in data:
        combined_text = f"Chapitre {quest['chapter']} dans {quest['region']} : \n{quest['quest_name']}\n{quest['abstract']}\n"
        labels = {quest['chapter'], quest['region']}
        for dialogue in quest['dialogs']:
            combined_text += f"{dialogue['name']}: {dialogue['text']}\n"
            labels.add(dialogue['name'])
        tokenized_data = tokenizer(combined_text.strip(), truncation=True, max_length=512, padding="max_length")
        train_data.append({
            "input_ids": tokenized_data["input_ids"][:-1],
            "attention_mask": tokenized_data["attention_mask"][:-1],
            "labels" : tokenized_data["input_ids"][:-1],
        })
    return train_data


def get_label_id(label: str):
    global _labels
    if label not in _labels:
        _labels[label] = len(_labels)
    return _labels[label]


if __name__ == "__main__":
    tokenizer = AutoTokenizer.from_pretrained(hf_model)
    tokenizer.pad_token = tokenizer.eos_token

    if os.path.exists(dataset_path):
        print(f"Loading dataset from {dataset_path}")
        train_dataset = Dataset.load_from_disk(dataset_path=dataset_path)
    else:
        train_datatoken = build_train_data(input_json_dataset, tokenizer)
        train_dataset = Dataset.from_list(train_datatoken)
        train_dataset.save_to_disk(dataset_path)
        print(f"saved dataset in file {dataset_path}, restart script again to load this file")
        sys.exit(0)

    accelerator = Accelerator(
        split_batches=2,
        gradient_accumulation_steps=8,
        cpu=False,
        step_scheduler_with_optimizer=True,
        mixed_precision="fp16")
    
    model = AutoModelForCausalLM.from_pretrained(hf_model, quantization_config=BitsAndBytesConfig(load_in_8bit=True))
    
    lora_config = LoraConfig(
        target_modules=["q_proj", "v_proj"],
        init_lora_weights=False
    )
    model.add_adapter(lora_config, adapter_name="adapter_1")
    model.gradient_checkpointing_enable()
    model = accelerator.prepare_model(model)
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir="./cerbinou_model",
            eval_strategy="no",
            learning_rate=2e-5,
            per_device_train_batch_size=2,  # Reduce if memory is an issue
            gradient_accumulation_steps=8,
            num_train_epochs=3,
            weight_decay=0.01,
            save_strategy="epoch",
            push_to_hub=False,
            label_names=["labels"],
            fp16=True,
            bf16=False
        ),
        train_dataset=train_dataset
    )
    trainer.train()
    
    model.save_pretrained("./cerbinou_model")
    tokenizer.save_pretrained("./cerbinou_model")