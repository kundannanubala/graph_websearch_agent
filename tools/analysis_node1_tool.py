import textstat
from wordfreq import word_frequency
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from langchain_core.messages import HumanMessage
import json
import spacy

# Load spaCy model (make sure it's loaded only once in your application)
nlp = spacy.load("en_core_web_sm")

def improved_grammar_check(text):
    errors = []
    doc = nlp(text)

    for sent in doc.sents:
        # Check for subject-verb agreement
        subject = None
        verb = None
        for token in sent:
            if token.dep_ == "nsubj":
                subject = token
            if token.pos_ == "VERB":
                verb = token
            if subject and verb:
                if subject.tag_ == "NNS" and verb.tag_ == "VBZ":
                    errors.append(f"Subject-verb disagreement: '{subject}' (plural) with '{verb}' (singular)")
                elif subject.tag_ == "NN" and verb.tag_ == "VBP":
                    errors.append(f"Subject-verb disagreement: '{subject}' (singular) with '{verb}' (plural)")
                break

        # Check for incorrect verb forms
        for token in sent:
            if token.text == "consist" and token.pos_ == "VERB":
                errors.append(f"Incorrect verb form: 'consist' should be 'consists'")
            if token.text == "have" and token.pos_ == "VERB" and token.head.pos_ != "VERB":
                errors.append(f"Incorrect verb form: 'have' should be 'has'")

        # Check for common mistakes
        text = sent.text.lower()
        if "there " in text and "shape" in text:
            errors.append("Incorrect use of 'there'. Did you mean 'their'?")
        if "then" in text and "than" not in text:
            errors.append("Possible confusion between 'then' and 'than'")
        if "it's" in text and "pointedness" in text:
            errors.append("Incorrect use of 'it's'. Did you mean 'its'?")

    return errors

def analysis_node1_tool(state):
    # Extract preprocessed data from the HumanMessage object
    preprocessed_data_message = state["preprocessed_data"][0]
    preprocessed_data = json.loads(preprocessed_data_message.content)

    text = preprocessed_data["text"]
    words = preprocessed_data["words"]
    sentences = preprocessed_data["sentences"]

    # Improved grammar checking
    grammar_errors = improved_grammar_check(text)

    # Readability analysis
    readability_score = textstat.flesch_reading_ease(text)

    # Vocabulary assessment
    vocab_complexity = np.mean([word_frequency(word, 'en') for word in words])

    # Sentence similarity
    similarity_scores = []
    for i in range(len(sentences)):
        for j in range(i+1, len(sentences)):
            similarity = SequenceMatcher(None, sentences[i], sentences[j]).ratio()
            similarity_scores.append(similarity)

    # TF-IDF similarity
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)
    tfidf_similarity = np.mean(cosine_similarity(tfidf_matrix))

    analysis_results = {
        "grammar_errors": grammar_errors,
        "readability_score": readability_score,
        "vocab_complexity": vocab_complexity,
        "sentence_similarities": similarity_scores,
        "average_sentence_similarity": np.mean(similarity_scores),
        "tfidf_similarity": tfidf_similarity
    }

    # Store analysis_results into a file (if needed)
    with open("D:/VentureInternship/AI Agent/ProjectK/analysis_node1_results.json", 'w') as file:
        json.dump(analysis_results, file, indent=4)

    with open("D:/VentureInternship/AI Agent/ProjectK/response.txt", "a") as file:
        file.write(f"\nAnalysis_Node1_Tool")

    # Update state with the correct message structure
    if "analysis_node1_response" not in state:
        state["analysis_node1_response"] = []
    state["analysis_node1_response"].append(
        HumanMessage(role="system", content=json.dumps(analysis_results))
    )

    return {"analysis_node1_response": state["analysis_node1_response"]}