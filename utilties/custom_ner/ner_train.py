import json
import random
from pathlib import Path
import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding

# Load training data and convert to spaCy Example format (only SKILL entities)
def load_data(file_path, nlp):
    with open(file_path, 'r', encoding="utf-8") as f:
        raw_data = json.load(f)

    training_examples = []

    for item in raw_data:
        text = item["text"]
        # Only keep SKILL-labeled entities
        entities = [(start, end, label) for start, end, label in item["entities"] if label == "SKILL"]
        if not entities:
            continue  # Skip samples with no SKILL labels
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, {"entities": entities})
        training_examples.append(example)

    return training_examples, {"SKILL"}

# Train the NER model
def train_ner(training_data, labels, iterations=20, model=None, output_dir="skill_ner_model"):
    if model:
        nlp = spacy.load(model)
        print(f"Loaded model '{model}'")
    else:
        nlp = spacy.blank("en")
        print("Created blank 'en' model")

    # Add NER pipe if not present
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # Add entity labels to NER
    for label in labels:
        ner.add_label(label)

    # Only train NER
    unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*unaffected_pipes):
        optimizer = nlp.begin_training()
        for i in range(iterations):
            random.shuffle(training_data)
            losses = {}
            batches = minibatch(training_data, size=compounding(4.0, 32.0, 1.5))
            for batch in batches:
                nlp.update(batch, drop=0.3, losses=losses)
            print(f"Iteration {i+1}/{iterations} - Losses: {losses}")

    # Save model
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(output_dir)
    print(f"Saved model to {output_dir.resolve()}")

# Main execution
if __name__ == "__main__":
    data_path = r"data\dataturks_resume_ner.json"  # Make sure this is a raw string
    temp_nlp = spacy.blank("en")
    training_data, labels = load_data(data_path, temp_nlp)
    train_ner(training_data, labels, iterations=100, model=None, output_dir=r"model\skill_ner_model")
