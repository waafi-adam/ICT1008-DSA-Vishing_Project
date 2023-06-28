import pandas as pd
import string
import re

# Load your dataset
df = pd.read_csv('raw_dataset.csv')

# Function to preprocess text
def preprocess_text(text):
    # Convert to lower case
    text = text.lower()

    # Remove salutations and names following them
    text = re.sub(r'(mr|mrs|ms|miss|dr|prof|officer)\.\s+\w+', '', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Tokenize - convert from string to list of words
    tokens = text.split()

    # Filter out stopwords, greetings, pronouns
    with open('stopwords_greetings_pronouns.txt', 'r') as f:
        stop_words = f.read().splitlines()
    words = [w for w in tokens if not w in stop_words]

    return words

# Apply the function to the Transcript column
df['Transcript'] = df['Transcript'].apply(preprocess_text)

# Save the cleaned dataset to a new CSV file
df.to_csv('cleaned_file.csv', index=False)
