import pandas as pd
import glob

file_list = glob.glob('Dataset/Translated/*.csv')

combined_data = pd.DataFrame()
dataframes = []

for file in file_list:
    
    data = pd.read_csv(file)
    dataframes.append(data)
    combined_data = pd.concat(dataframes, ignore_index=True)

combined_data.to_csv('df_combined.csv', index=False)
