from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import spacy
from nltk.corpus import stopwords
import string
import re
from cosine_sim import calculate_similarity


def preprocess_sentence(sentence):
    # Remove special characters
    sentence = re.sub(r"[^\w\s']", "", sentence)
    # Tokenize the sentence into words
    tokens = word_tokenize(sentence)
    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in tokens if token.lower() not in stop_words]
    # Remove punctuations
    tokens = [token for token in tokens if token not in string.punctuation]
    # Join the tokens back into a sentence string
    preprocessed_sentence = " ".join(tokens)
    # Manually remove single quotation marks
    preprocessed_sentence = preprocessed_sentence.replace("'", "")
    return preprocessed_sentence


nlp = spacy.load("en_core_web_lg")

# Load the fraud dataset
fraudDataSet = pd.read_csv("preprocessfraudtest.csv")
# Load the non-fraud dataset
nonFraudDataSet = pd.read_csv("preprocessnonfraudtest.csv")

# Define the reference sentence
refSentence = "i am irs. give me username and password"
preprocessedRefSentence = preprocess_sentence(refSentence)

maxFraudSimilarity = 0.0
# Iterate through each row of the fraud dataset
for index, row in fraudDataSet.iterrows():
    sentence = row["text"]
    similarity = calculate_similarity(sentence, preprocessedRefSentence)
    if similarity > maxFraudSimilarity:
        maxFraudSimilarity = similarity

print("Max fraud similarity:", maxFraudSimilarity)

maxNonFraudSimilarity = 0.0
# Iterate through each row of the non-fraud dataset
for index, row in nonFraudDataSet.iterrows():
    sentence = row["text"]
    similarity = calculate_similarity(sentence, preprocessedRefSentence)
    if similarity > maxNonFraudSimilarity:
        maxNonFraudSimilarity = similarity

print("Max non-fraud similarity:", maxNonFraudSimilarity)

# Calculate the percentage similarity
fraudPercentage = maxFraudSimilarity * 100
nonFraudPercentage = maxNonFraudSimilarity * 100

print("Fraud percentage similarity:", fraudPercentage)
print("Non-fraud percentage similarity:", nonFraudPercentage)

# Predict the likelihood of vishing attempt based on the maximum similarity
prediction = fraudPercentage / (fraudPercentage + nonFraudPercentage) * 100
print("Vishing prediction:", prediction)
