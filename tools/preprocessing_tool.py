import spacy
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from langchain_core.messages import HumanMessage
import json

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def preprocessing_tool(state):
    user_input = state["user_input"]

    # Tokenization
    words = word_tokenize(user_input)
    sentences = sent_tokenize(user_input)

    # SpaCy processing
    doc = nlp(user_input)

    # POS tagging
    pos_tags = [(token.text, token.pos_) for token in doc]

    # Named Entity Recognition
    named_entities = [(ent.text, ent.label_) for ent in doc.ents]

    preprocessed_data = {
        "text": user_input,
        "words": words,
        "sentences": sentences,
        "pos_tags": pos_tags,
        "named_entities": named_entities
    }

    # Store preprocessed_data into a file (if needed)
    with open("D:/VentureInternship/AI Agent/ProjectK/preprocessed_data.json", 'w') as file:
        json.dump(preprocessed_data, file, indent=4)

    with open("D:/VentureInternship/AI Agent/ProjectK/response.txt", "w") as file:
        file.write(f"\nPreprocessing_Tool")

    # Update state with the correct message structure
    state["preprocessed_data"] = [
        HumanMessage(role="system", content=json.dumps(preprocessed_data))
    ]

    return {"preprocessed_data": state["preprocessed_data"]}