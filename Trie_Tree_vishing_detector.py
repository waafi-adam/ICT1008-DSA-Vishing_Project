import pandas as pd
import string
import re
from collections import Counter
import csv

# Define TrieNode and Trie
class TrieNode:
    def __init__(self):
        self.children = {}
        self.end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.end_of_word = True

    def search(self, word):
        current = self.root
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        return current.end_of_word

    def print_trie(self, root=None, word=''):
        if root is None:
            root = self.root
        for k, v in root.children.items():
            if v.end_of_word:
                print(word + k)
            self.print_trie(v, word + k)

    def count_words(self, node=None):
        if node is None:
            node = self.root
        count = 1 if node.end_of_word else 0
        for child in node.children.values():
            count += self.count_words(child)
        return count

# Function to preprocess and tokenize text
def tokenize_text(text):
    text = text.lower()
    text = re.sub(r'(mr|mrs|ms|miss|dr|prof|officer)\.\s+\w+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    with open('stopwords_greetings_pronouns.txt', 'r') as f:
        stop_words = f.read().splitlines()
    words = [w for w in tokens if not w in stop_words]
    return words, len(tokens)

spam_df = pd.read_csv('spam_dataset.csv')
nonspam_df = pd.read_csv('non_spam_dataset.csv')

spam_df['Transcript'], spam_df['Word_Count'] = zip(*spam_df['Transcript'].apply(tokenize_text))
nonspam_df['Non_Spams'], nonspam_df['Word_Count'] = zip(*nonspam_df['Non_Spams'].apply(tokenize_text))

spam_word_freq = Counter()
nonspam_word_freq = Counter()
for index, row in spam_df.iterrows():
    spam_word_freq.update(row['Transcript'])
for index, row in nonspam_df.iterrows():
    nonspam_word_freq.update(row['Non_Spams'])

for word in nonspam_word_freq:
    if word in spam_word_freq:
        del spam_word_freq[word]

top_n = 30
spam_types = spam_df['Spam_Type'].unique()
top_words = {spam_type: Trie() for spam_type in spam_types}

sum_freq_top_words = 0

for spam_type in spam_types:
    spam_type_words = spam_df[spam_df['Spam_Type'] == spam_type]['Transcript'].explode()
    top_spam_type_words = spam_type_words.value_counts().head(top_n)
    for word, freq in top_spam_type_words.items():
        top_words[spam_type].insert(word)
        sum_freq_top_words += freq


# Print the Trie structure
for spam_type, trie in top_words.items():
    print(f"Spam Type: {spam_type}")
    print("Trie Structure:")
    trie.print_trie()
    print()

# Calculate total words
total_words_spam = spam_df['Word_Count'].sum()

test_cases = []
with open('test_cases.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        test_cases.append(row)

# sum_freq_top_words = sum(trie.count_words() for trie in top_words.values())  


perc_top_words_spam = (sum_freq_top_words / total_words_spam) * 100

accuracy_sum = 0
total_datasets = len(test_cases)

for idx, test_case in enumerate(test_cases, 1):
    input_sample, expected_label = test_case[1], test_case[2]
    text = re.sub(r'\W+', ' ', input_sample.lower())
    total_matches = 0
    spam_type_matches = {spam_type: 0 for spam_type in spam_types}

    for word in text.split():
        for spam_type in spam_types:
            if top_words[spam_type].search(word):
                total_matches += 1
                spam_type_matches[spam_type] += 1

    perc_matches = (total_matches / len(text.split())) * 100 if total_matches else 0
    spam_likelihood = (perc_matches / perc_top_words_spam) * 100
    spam_likelihood = max(0, min(100, spam_likelihood))

    most_likely_spam_type = max(spam_type_matches, key=spam_type_matches.get)

    predicted_label = "Vishing" if spam_likelihood >= 50 else "Not Vishing"
    if predicted_label == expected_label:
        accuracy_sum += 1

    print(f"Test Case {idx}:")
    print(f"Text: {input_sample}")
    print(f"Expected Label: {expected_label}")
    print(f"Predicted Label: {predicted_label}")
    if predicted_label == "Spam":
        print(f"Predicted Spam Type: {most_likely_spam_type}")
    print(f"Spam Likelihood: {spam_likelihood:.2f}%")
    print()

avg_accuracy = (accuracy_sum / total_datasets) * 100
print(f"Average Accuracy: {avg_accuracy:.2f}%")
