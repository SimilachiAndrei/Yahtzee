import random as rand
import matplotlib.pyplot as plt
from langdetect import detect
import rowordnet as rwn
from rake_nltk import Rake
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt')
nltk.download('wordnet')


def detect_language(text):
    try:
        lang = detect(text)
        print(f"Detected Language: {lang}")
        return lang
    except Exception as e:
        print(f"Language Detection Error: {e}")
        return None

def stylometric(text):
    words = nltk.word_tokenize(text)
    no_punct = [token for token in words if any(c.isalpha() for c in token)]
    print("Length in words: " + str(len(no_punct)))
    print("Length in characters: " + str(sum(len(token) for token in no_punct)))
    freq = {}
    for word in no_punct:
        if word.lower() not in freq:
            freq[word.lower()] = 1
        else:
            freq[word.lower()] += 1
    token_lengths = [len(token) for token in no_punct]
    words_by_length = nltk.FreqDist(token_lengths)
    print("Word frequency:\n" + str(freq))

    words_by_length.plot(15, title="Stylometry")
    plt.xlabel("Word Length")
    plt.ylabel("Frequency")
    plt.show()

def alternate_ver(text):
    wn = rwn.RoWordNet()
    words = nltk.word_tokenize(text)
    no_punct = [token for token in words if any(c.isalpha() for c in token)]
    counter = 0
    replaced_text = []

    for token in words:
        if any(c.isalpha() for c in token):
            synset_ids = wn.synsets(token.lower())
            syns = set()
            if len(token) > 3:
                for synset_id in synset_ids:
                    outbound_relations = wn.relations(synset_id)
                    for outbound_relation in outbound_relations:
                        target_synset_id = outbound_relation[0]
                        relation = outbound_relation[1]
                        if relation in {"hypernym", "similar_to"}:
                            syns.update(wn.synset(target_synset_id).literals)
                        elif relation == "near_antonym":
                            lits = wn.synset(target_synset_id).literals
                            modified_lits = {"nu " + lit for lit in lits}
                            syns.update(modified_lits)
                if syns:
                    random_word = rand.choice(list(syns))
                    print(token + " - Synonym: " + random_word)
                    replaced_text.append(random_word)
                    counter += 1
                else:
                    print(token + ": No synonyms found")
                    replaced_text.append(token)
            else:
                replaced_text.append(token)
        else:
            replaced_text.append(token)

    modified_text = " ".join(replaced_text)

    modified_text = modified_text.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")

    print(f"\nOriginal word count: {len(no_punct)}")
    print(f"Words replaced: {counter}")
    print("\nModified Text:\n" + modified_text)


def extract_and_modify_propositions(text):
    rake_nltk_var = Rake(max_length=1)

    rake_nltk_var.extract_keywords_from_text(text)
    keywords = rake_nltk_var.get_ranked_phrases()

    print("Keywords:")
    print(keywords)

    propositions = []

    wn = rwn.RoWordNet()

    for keyword in keywords:
        sentences = sent_tokenize(text)

        for sentence in sentences:
            if keyword in sentence:
                modified_sentence = []
                words = nltk.word_tokenize(sentence)

                for word in words:
                    if word.lower() != keyword.lower():
                        synset_ids = wn.synsets(word.lower())
                        syns = set()
                        if len(word) > 4:
                            for synset_id in synset_ids:
                                outbound_relations = wn.relations(synset_id)
                                for outbound_relation in outbound_relations:
                                    target_synset_id = outbound_relation[0]
                                    relation = outbound_relation[1]
                                    # if relation in {"hypernym", "similar_to"}:
                                    #     syns.update(wn.synset(target_synset_id).literals)
                                    # elif relation == "near_antonym":
                                    #     lits = wn.synset(target_synset_id).literals
                                    #     modified_lits = {"nu " + lit for lit in lits}
                                    #     syns.update(modified_lits)
                                    syns.update(wn.synset(target_synset_id).literals)
                            if syns:
                                random_word = rand.choice(list(syns))
                                modified_sentence.append(random_word)
                            else:
                                modified_sentence.append(word)
                        else:
                            modified_sentence.append(word)
                    else:
                        modified_sentence.append(word)

                modified_sentence = " ".join(modified_sentence)
                modified_sentence = modified_sentence.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(
                    " ?", "?")

                propositions.append(modified_sentence)
                break

    print("\nModified Propositions:")
    for i, proposition in enumerate(propositions):
        print(f"{i + 1}. {proposition}")


text = ""
try:
    with open("text.txt", 'r', encoding='utf-8') as file:
        text = file.read()
except FileNotFoundError:
    print("Error: text.txt not found.")
    exit()
except UnicodeDecodeError:
    print("Error: Could not decode text.txt. Please check the encoding.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit()

# detect_language(text)
# stylometric(text)
# alternate_ver(text)
extract_and_modify_propositions(text)