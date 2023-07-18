import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

#Removing Punctuation
def removePunctuations(text):
    text = re.sub(r'[^\w\s]','',text)
    return text

#Splitting words
def tokenize(text):
    return word_tokenize(text)

#Removing stopwords
def removeStopwords(text):
    stop_words = stopwords.words('english')
    return [word for word in text if word.lower() not in stop_words]

#Lemmatizing words
def lemma(text):
    return [WordNetLemmatizer().lemmatize(word) for word in text]

data = pd.read_csv('df_data.csv')

data['Words'] = data['translated_words'].apply(lambda x: removePunctuations(x))

nltk.download('punkt')
nltk.download('wordnet')
data['Words'] = data['Words'].apply(tokenize)

nltk.download('stopwords')
data['Words'] = data['Words'].apply(removeStopwords)

data['Words'] = data['Words'].apply(lemma)

data.to_csv('df_processed.csv', index=False)

print('Save data to df_processed')


filtered_data = data[data['Label'] == 1]


tokens_list = []
for element in filtered_data['Words']:
    tokens_list.extend(element)

word_counts = pd.Series(tokens_list).value_counts()

print(word_counts.head(20))
