import os
import json
import pandas as pd
from openai import OpenAI

def get_review_data():
    with open('scraped_reviews.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    return df

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        # "text-embedding-ada-002",
        # "text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def save_embedding_dict(df):
    embedding_dict = df.apply(lambda row: {
        'Title': row['Title'],
        'Nose_embedding': row['Nose_embedding'],
        'Palate_embedding': row['Palate_embedding'],
        'Finish_embedding': row['Finish_embedding'],
        'Comment_embedding': row['Comment_embedding']
    }, axis=1).tolist()
    with open('embedded_dict.json', 'w', encoding='utf-8') as f:
        json.dump(embedding_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":

    # OpenAI APIキーの設定
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # DataFrameの作成
    df = get_review_data()

    # テイスティングコメントのテキストをベクトル化
    for column in ['Nose', 'Palate', 'Finish', 'Comment']:
        print(f'{column}のベクトル化中...')
        df[f'{column}_embedding'] = df[column].apply(get_embedding)

    save_embedding_dict(df)
