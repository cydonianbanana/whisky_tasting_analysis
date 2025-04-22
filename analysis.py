import os
import json
import pandas as pd
import numpy as np
from openai import OpenAI
from sklearn.decomposition import PCA
import plotly.express as px

def get_review_data():
    with open('reviews.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    return df

def convert_numeric_columns(df):
    numeric_columns = ['ABV', 'Age', 'Score']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        # "text-embedding-ada-002",
        # "text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def save_embeding_dict(df):
    embeding_dict = df.apply(lambda row: {
        'title': row['title'],
        'Nose_embedding': row['Nose_embedding'],
        'Palate_embedding': row['Palate_embedding'],
        'Finish_embedding': row['Finish_embedding'],
        'Comment_embedding': row['Comment_embedding']
    }, axis=1).tolist()
    with open('embeding_dict.json', 'w', encoding='utf-8') as f:
        json.dump(embeding_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":

    # OpenAI APIキーの設定
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # DataFrameの作成
    df = get_review_data()

    # 数値カラムの変換
    df = convert_numeric_columns(df)

    # テイスティングコメントのテキストをベクトル化
    for column in ['Nose', 'Palate', 'Finish', 'Comment']:
        print(f'{column}のベクトル化中...')
        df[f'{column}_embedding'] = df[column].apply(get_embedding)

    save_embeding_dict(df)
    quit()

    # ベクトルをnumpy配列に変換
    embeddings = np.array(df['Nose_embedding'].tolist())

    # PCAによる次元削減
    pca = PCA(n_components=3)
    reduced_embeddings = pca.fit_transform(embeddings)

    # 結果をDataFrameに追加
    df['x'] = reduced_embeddings[:, 0]
    df['y'] = reduced_embeddings[:, 1]
    df['z'] = reduced_embeddings[:, 2]

    # 3Dプロットの作成
    fig = px.scatter_3d(
        df,
        x='x',
        y='y',
        z='z',
        color='Score',
        hover_data=['Name', 'Nose'],
        title='ウイスキーの香りの3D可視化'
    )

    # プロットの表示
    fig.show()
