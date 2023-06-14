import googletrans
from googletrans import Translator
from googletrans import LANGUAGES
import pandas as pd
import ftfy
import io
import numpy as np
import json

# Using googletrans to create class
translator = Translator()

# Define file path
file_path = 'df_data_raw.csv'

# Read csv file with different encodings
encodings = ['utf-8', 'latin-1', 'utf-16', 'utf-32']
for encoding in encodings:
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
        break
    except UnicodeDecodeError:
        continue
else:
    raise Exception(
        "Unable to decode the file using any of the specified encodings.")

# Fixed encoding issues
fixed_content = ftfy.fix_text(content)

# Create dataframe
df = pd.read_csv(io.StringIO(fixed_content))

df.columns = ['Transcript', 'Label']

print(df)
translated_words = []
full_source_language = []

# Using for loop to perform the translation and append to the list
for element in df['Transcript']:
    try:
        translation = translator.translate(element)
        translated_text = translation.text
        source_language = LANGUAGES.get(translation.src)
    except TypeError:
        translation = None
        translated_text = ''
        source_language = ''

    translated_words.append(translated_text)
    full_source_language.append(source_language)

df['translated_words'] = translated_words
df['full_source_language'] = full_source_language

# Save the df to a new CSV file
df.to_csv("df_translated.csv", header=True, index=False)
