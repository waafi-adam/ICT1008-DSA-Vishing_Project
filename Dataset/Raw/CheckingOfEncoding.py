import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        print(f"Detected encoding: {encoding} (confidence: {confidence})")

file_path = 'df_data_vishing.csv'
detect_encoding(file_path)
