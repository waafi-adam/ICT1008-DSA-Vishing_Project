import pandas as pd
import string
import re
from collections import Counter
import csv
import pprint

# Function to preprocess and tokenize text
def tokenize_text(text):
    # Convert to lower case
    text = text.lower()

    # Remove salutations and names following them
    text = re.sub(r'(mr|mrs|ms|miss|dr|prof|officer)\.\s+\w+', '', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Tokenize - convert from string to list of words
    tokens = text.split()

    # Calculate total number of tokens before removing stop words
    word_count = len(tokens)

    # Filter out stopwords, greetings, pronouns
    with open('stopwords_greetings_pronouns.txt', 'r') as f:
        stop_words = f.read().splitlines()
    words = [w for w in tokens if not w in stop_words]

    return words, word_count

# Function to calculate word frequencies
def calculate_frequencies(df, column):
    word_freq = Counter()
    for index, row in df.iterrows():
        word_freq.update(row[column])
    return word_freq

# Function to prepare failure function for KMP
def prepare_failure_function(word):
    failure = [0]
    j = 0
    for i in range(1, len(word)):
        while j > 0 and word[i] != word[j]:
            j = failure[j-1]
        if word[i] == word[j]:
            j += 1
        failure.append(j)
    return failure

# Load the datasets
spam_df = pd.read_csv('spam_dataset.csv')
nonspam_df = pd.read_csv('non_spam_dataset.csv')

# Preprocess and tokenize text
spam_df['Transcript'], spam_df['Word_Count'] = zip(*spam_df['Transcript'].apply(tokenize_text))
nonspam_df['Non_Spams'], nonspam_df['Word_Count'] = zip(*nonspam_df['Non_Spams'].apply(tokenize_text))

# Calculate total words
total_words_spam = spam_df['Word_Count'].sum()
total_words_nonspam = nonspam_df['Word_Count'].sum()

# Calculate word frequencies
spam_word_freq = calculate_frequencies(spam_df, 'Transcript')
nonspam_word_freq = calculate_frequencies(nonspam_df, 'Non_Spams')

# Remove common words from the spam word frequencies based on the non-spam word frequencies
for word in nonspam_word_freq:
    if word in spam_word_freq:
        del spam_word_freq[word]

# Get top 20 words for each spam type
top_n = 30
spam_types = spam_df['Spam_Type'].unique()
top_words = {spam_type: {} for spam_type in spam_types}

for spam_type in spam_types:
    # Filter spam words by spam type
    spam_type_words = spam_df[spam_df['Spam_Type'] == spam_type]['Transcript'].explode()
    # Count the word frequencies and get the top n words
    top_spam_type_words = spam_type_words.value_counts().head(top_n)

    for word, freq in top_spam_type_words.items():
        # Prepare failure function for KMP
        failure_function = prepare_failure_function(word)
        top_words[spam_type][word] = {'freq': freq, 'failure_function': failure_function}

# Remove shared words from the top_words and add them to the shared_spam_words category
shared_spam_words = {}

for spam_type in spam_types:
    for word in list(top_words[spam_type].keys()):
        shared = False
        for other_spam_type in spam_types:
            if other_spam_type != spam_type and (word in top_words[other_spam_type] or word in shared_spam_words):
                shared_spam_words[word] = top_words[spam_type].pop(word)
                shared = True
                break
        if shared:
            top_words[spam_type] = dict(top_words[spam_type])  # Convert back to regular dictionary

# Add shared_spam_words category to top_words
top_words['shared_spam_words'] = shared_spam_words

# Now the top_words dictionary contains the top 20 words for each spam type and shared_spam_words

# Print the top_words dictionary with formatting

pp = pprint.PrettyPrinter(indent=4)

for spam_type, words_info in top_words.items():
    print(f"Spam Type: {spam_type}")
    print("Top Words:")
    for word in words_info.keys():
        print(word)
    print()

# Now you can use `top_words` dictionary in your further analysis

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

# Calculate the sum of the word frequencies in top_words
sum_freq_top_words = sum(word_info['freq'] for spam_type in top_words for word_info in top_words[spam_type].values())

# Calculate the percentages
perc_top_words_spam = (sum_freq_top_words / total_words_spam) * 100

def detect_vishing(input_sample: str):
    # Preprocess and tokenize text
    # Don't forget to load your datasets here if you haven't done so globally
    # You should probably cache your datasets and top_words after initial load

    # Prepare text input
    text = re.sub(r'\W+', ' ', input_sample.lower())
    total_matches = 0
    spam_type_matches = {spam_type: 0 for spam_type in spam_types}

    # Apply KMP algorithm to each word in our `top_words` object
    for spam_type in spam_types:
        for word, word_info in top_words[spam_type].items():
            matches = kmp_search(text, word, word_info['failure_function'])
            total_matches += matches
            spam_type_matches[spam_type] += matches

    # Calculate percentage of matches
    perc_matches = (total_matches / len(text.split())) * 100 if total_matches else 0

    # Determine spam likelihood based on comparison with calculated percentage for top spam words
    spam_likelihood = (perc_matches / perc_top_words_spam) * 100
    # Ensuring the percentage stays in the range [0, 100]
    spam_likelihood = max(0, min(100, spam_likelihood))

    # Identify most likely spam type
    most_likely_spam_type = max(spam_type_matches, key=spam_type_matches.get)

    # Determine the predicted label
    predicted_label = "Vishing" if spam_likelihood >= 50 else "Not Vishing"

    return predicted_label, spam_likelihood, most_likely_spam_type

if __name__ == "__main__":
    # This will only be executed when you run this script directly
    # and not when you import from another script.
    test_cases = []
    with open('test_cases.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            test_cases.append(row)

    # Initialize accuracy and total datasets
    accuracy_sum = 0
    total_datasets = len(test_cases)

    # Loop through test cases
    for idx, test_case in enumerate(test_cases, 1):
        input_sample, expected_label = test_case[1], test_case[2]
        predicted_label, spam_likelihood, most_likely_spam_type = detect_vishing(input_sample)

        # Check if the predicted label matches the expected label
        if predicted_label == expected_label:
            accuracy_sum += 1

        print(f"Test Case {idx}:")
        print(f"Text: {input_sample}")
        print(f"Expected Label: {expected_label}")
        print(f"Predicted Label: {predicted_label}")
        if predicted_label == "Vishing":
            print(f"Predicted Spam Type: {most_likely_spam_type}")
        print(f"Spam Likelihood: {spam_likelihood}")
        print()

    # Calculate average accuracy
    avg_accuracy = (accuracy_sum / total_datasets) * 100

    print(f"Average Accuracy: {avg_accuracy:.2f}%")