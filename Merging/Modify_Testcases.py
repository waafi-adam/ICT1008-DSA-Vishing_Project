import pandas as pd

df = pd.read_csv('Project/cs/Dataset/df_data.csv')

df.index = range(101, 101 + len(df)) 

df['Label'] = df['Label'].map({1: 'Vishing', 0: 'Not Vishing'})

df = df.rename(
    columns={'translated_words': 'Transcript'})

df.to_csv('Project/cs/Merging/modified_testcases.csv', index_label='Index')
