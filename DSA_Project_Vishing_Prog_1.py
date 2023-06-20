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
fraudDataSet = pd.read_csv("fraudtest.csv")
# Preprocess the "text" column using the preprocess_sentence function
fraudDataSet["text"] = fraudDataSet["text"].apply(preprocess_sentence)
# Save the preprocessed dataset to a new CSV file
fraudDataSet.to_csv("preprocessfraudtest.csv", index=False, columns=["id", "text"])

# Load the non-fraud dataset
nonFraudDataSet = pd.read_csv("nonfraudtest.csv")
# Preprocess the "text" column using the preprocess_sentence function
nonFraudDataSet["text"] = nonFraudDataSet["text"].apply(preprocess_sentence)
# Save the preprocessed dataset to a new CSV file
nonFraudDataSet.to_csv(
    "preprocessnonfraudtest.csv", index=False, columns=["id", "text"]
)


# Define the reference sentence
refSentence = "i am the irs, give me username and password"
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

# print("Average fraud similarity:", avgFraudSimilarity)

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

# print("Average non-fraud similarity:", avgNonFraudSimilarity)

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

# prediction = normalizedFraudSimilarity * 100
# print("Vishing prediction:", prediction)

# ======================================================================

if normalizedFraudSimilarity > 0 and normalizedNonFraudSimilarity < 1:
    refSentence = nlp(refSentence)
    fraudDataSet = [nlp(row) for row in fraudDataSet["text"]]

    sims = []
    docId = []
    for i in range(len(fraudDataSet)):
        sentence = row["text"]
        # Preprocess the sentence
        preprocessedSentence = preprocess_sentence(sentence)
        # Calculate similarity using spaCy
        similarity = nlp(preprocessedSentence).similarity(nlp(preprocessedRefSentence))
        sims.append(similarity)
        docId.append(index)

    # Create a DataFrame to store document IDs and similarity scores
    simsDocs = pd.DataFrame(list(zip(docId, sims)), columns=["doc_id", "similarity"])

    # Calculate the total percentage value
    total_similarity_percentage = sum(sims) / len(sims) * 100

    print("Total similarity percentage:", total_similarity_percentage)
