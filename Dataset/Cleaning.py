import pandas as pd

data = pd.read_csv('df_data.csv')

# Drop rows with null values
data = data.dropna()

# Drop useless columns 
data = data.drop(columns=['Transcript', 'full_source_language'])

df = pd.DataFrame(data, columns= ['Label','translated_words'])
df = df[['translated_words','Label']]

df.to_csv('df_data.csv', index=False)
