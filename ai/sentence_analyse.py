import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('stopwords')


def count_clauses(sentence):
    # Identify clause count using simple sentence segmentation
    words = word_tokenize(sentence)
    tagged = pos_tag(words)

    independent_clause_count = 0
    dependent_clause_count = 0
    conjunctions = {"and", "or", "but", "so", "for", "nor", "yet"}
    subordinating_conjunctions = {"when", "because", "if", "although", "since", "while", "after", "before", "unless",
                                  "whereas"}

    for word, tag in tagged:
        if word.lower() in conjunctions:
            independent_clause_count += 1
        elif word.lower() in subordinating_conjunctions:
            dependent_clause_count += 1

    # Adding one independent clause by default
    return independent_clause_count + 1, dependent_clause_count


def classify_sentence(sentence):
    independent_clause_count, dependent_clause_count = count_clauses(sentence)

    if independent_clause_count == 1 and dependent_clause_count == 0:
        return "Simple Sentence"
    elif independent_clause_count >= 2 and dependent_clause_count == 0:
        return "Compound Sentence"
    elif independent_clause_count >= 1 and dependent_clause_count >= 1:
        return "Complex Sentence"
    else:
        return "Unidentified Sentence Type"


def test_classifier(test_sentences):
    sentences_label = []
    for sentence in test_sentences:
        result = classify_sentence(sentence)
        # print(f"句子: {sentence}")
        # print(f"类型: {result}\n")
        sentences_label.append(result)
    return sentences_label


if __name__ == "__main__":
    test_sentences = [
        "I love programming.",
        "I love programming, and I enjoy coding.",
        "Although it was raining, I went to school because I had an exam.",
    ]
    label = test_classifier(test_sentences)
    print(label)
