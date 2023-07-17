import pandas as pd
import pprint

# Load the cleaned dataset
df = pd.read_csv('cleaned_file.csv')

# Convert the 'Transcript' column back to a list of words
df['Transcript'] = df['Transcript'].apply(eval)

# Create dictionaries to store word frequencies for each spam type
spam_types = df['Spam_Type'].unique()
word_freq = {spam_type: {} for spam_type in spam_types}

# Iterate over each row of the tokenized dataset
for index, row in df.iterrows():
    spam_type = row['Spam_Type']
    # Iterate over each word in the tokenized row
    for word in row['Transcript']:
        # Check if the word already exists in the dictionary for the specific spam type
        if word in word_freq[spam_type]:
            # Increment its frequency by 1
            word_freq[spam_type][word] += 1
        else:
            # Add the word to the dictionary with a frequency of 1
            word_freq[spam_type][word] = 1

# Print the top 20 most common words for each spam type in descending order
top_n = 20
for spam_type in spam_types:
    sorted_word_freq = sorted(word_freq[spam_type].items(), key=lambda x: x[1], reverse=True)
    word_freq[spam_type] = {word: freq for word, freq in sorted_word_freq[:top_n]}

def compute_failure_array(word):
    failure = [0] * len(word)
    j = 0  # Index for the pattern

    # Preprocess the pattern to calculate the failure function values
    for i in range(1, len(word)):
        if word[i] == word[j]:
            j += 1
            failure[i] = j
        else:
            if j != 0:
                j = failure[j - 1]
                i -= 1
            else:
                failure[i] = 0
    return failure

# Replace word frequencies with failure arrays
for spam_type in spam_types:
    for word in word_freq[spam_type]:
        word_freq[spam_type][word] = compute_failure_array(word)

pprint.pprint(word_freq)


####################################################
import re

# KMP search function
def kmp_search(text, pattern, failure):
    i, j = 0, 0
    matches = 0

    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
            if j == len(pattern):
                matches += 1
                j = failure[j - 1]
        else:
            if j != 0:
                j = failure[j - 1]
            else:
                i += 1
    return matches

# Input samples
input_samples = [
    "Hey John, hope you're doing well. Just wanted to touch base on our project. Can we have a meeting tomorrow?",
    "Congratulations on winning the annual employee award! I noticed some unusual activities in your performance, you've really stepped up your game this year!",
    "Congratulations! You've won our grand prize draw! Click the link below to claim your prize immediately. Hurry up!",
    "URGENT: Your credit card has been compromised. We detected multiple unauthorized transactions. Please call our hotline immediately to secure your account."
]

# Loop through input samples
for idx, input_sample in enumerate(input_samples, 1):
    # Prepare text input
    text = re.sub(r'\W+', ' ', input_sample.lower())
    total_matches = 0
    spam_type_matches = {spam_type: 0 for spam_type in spam_types}

    # Apply KMP algorithm to each word in our `word_freq` object
    for spam_type in spam_types:
        for word, failure in word_freq[spam_type].items():
            matches = kmp_search(text, word, failure)
            total_matches += matches
            spam_type_matches[spam_type] += matches

    # Calculate likelihood of spam based on the total matches found
    spam_likelihood = (total_matches / len(text.split())) * 100 if total_matches else 0

    # Identify most likely spam type
    most_likely_spam_type = max(spam_type_matches, key=spam_type_matches.get)

    print(f"Input Sample {idx}:")
    print(f"Text: {input_sample}")
    print(f"Likelihood of spam: {spam_likelihood:.2f}%")
    print(f"Most likely spam type: {most_likely_spam_type}")
    print()
