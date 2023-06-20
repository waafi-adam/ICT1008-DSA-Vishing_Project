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

totalFraudSimilarity = 0.0
numFraudSentences = 0
# Iterate through each row of the fraud dataset
for index, row in fraudDataSet.iterrows():
    sentence = row["text"]
    similarity = calculate_similarity(sentence, preprocessedRefSentence)
    totalFraudSimilarity += similarity
    numFraudSentences += 1

if numFraudSentences > 0:
    avgFraudSimilarity = totalFraudSimilarity / numFraudSentences
else:
    avgFraudSimilarity = 0.0

print("Average fraud similarity:", avgFraudSimilarity)

totalNonFraudSimilarity = 0.0
numNonFraudSentences = 0
# Iterate through each row of the non-fraud dataset
for index, row in nonFraudDataSet.iterrows():
    sentence = row["text"]
    similarity = calculate_similarity(sentence, preprocessedRefSentence)
    totalNonFraudSimilarity += similarity
    numNonFraudSentences += 1

if numNonFraudSentences > 0:
    avgNonFraudSimilarity = totalNonFraudSimilarity / numNonFraudSentences
else:
    avgNonFraudSimilarity = 0.0

print("Average non-fraud similarity:", avgNonFraudSimilarity)

# Normalize the similarity scores to the range [0, 1]
similarity_range = max(avgFraudSimilarity, avgNonFraudSimilarity) - min(
    avgFraudSimilarity, avgNonFraudSimilarity
)
if similarity_range > 0:
    normalizedFraudSimilarity = (
        avgFraudSimilarity - min(avgFraudSimilarity, avgNonFraudSimilarity)
    ) / similarity_range
    normalizedNonFraudSimilarity = (
        avgNonFraudSimilarity - min(avgFraudSimilarity, avgNonFraudSimilarity)
    ) / similarity_range
else:
    normalizedFraudSimilarity = 0.0
    normalizedNonFraudSimilarity = 0.0

print("Normalized fraud similarity:", normalizedFraudSimilarity)
print("Normalized non-fraud similarity:", normalizedNonFraudSimilarity)

# ======================================================================
