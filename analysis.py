import json
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import plotly.express as px

def get_review_data():
    with open('scraped_reviews.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    return df

def convert_numeric_columns(df):
    # ABVカラムの変換（パーセント記号を除去し、100で割る）
    df['ABV'] = df['ABV'].str.rstrip('%').astype(float) / 100
    
    # Ageカラムの変換（数値部分のみを抽出して整数に変換）
    # まず数値部分を抽出し、NaNの場合はNaNのまま保持
    age_extracted = df['Age'].str.extract('(\d+)')
    # 数値に変換可能な値のみを整数に変換
    df['Age'] = pd.to_numeric(age_extracted[0], errors='coerce').astype('Int64')  # Int64はNaNを許容する整数型
    
    # Scoreカラムの変換（数値部分のみを抽出して浮動小数点数に変換）
    df['Score'] = df['Score'].str.extract('(\d+\.?\d*)').astype(float)
    
    return df

def get_embedded_dict():
    with open('embedded_dict.json', 'r', encoding='utf-8') as f:
        embedded_dict = json.load(f)
    return embedded_dict

def plot_3d_scatter(df, column, embeddings):
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
        hover_data=['Title', column],
        title=f'ウイスキーの{column}の3D可視化',
        opacity=0.7  # 透明度を設定
    )

    # 点のサイズを小さく設定
    fig.update_traces(marker=dict(size=1))
    # HTMLファイルとして出力
    fig.write_html(f"plot_{column.lower()}_3d.html")

def plot_2d_scatter(df, column, embeddings):
    # PCAによる次元削減
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings)

    # 結果をDataFrameに追加
    df['x'] = reduced_embeddings[:, 0]
    df['y'] = reduced_embeddings[:, 1]

    # 2Dプロットの作成
    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='Score',
        hover_data=['Title', column],
        title=f'ウイスキーの{column}の2D可視化',
        opacity=0.7  # 透明度を設定
    )

    # 点のサイズを小さく設定
    fig.update_traces(marker=dict(size=5))
    # HTMLファイルとして出力
    fig.write_html(f"plot_{column.lower()}_2d.html")

def plot_2d_scatter_with_clusters(df, column, embeddings, n_clusters=5):
    # PCAによる次元削減
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings)

    # K-meansクラスタリング
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(reduced_embeddings)

    # 結果をDataFrameに追加
    df['x'] = reduced_embeddings[:, 0]
    df['y'] = reduced_embeddings[:, 1]
    df['Cluster'] = clusters

    # 2Dプロットの作成
    fig = px.scatter(
        df,
        x='x',
        y='y',
        color='Cluster',  # クラスターで色分け
        hover_data=['Title', column, 'Score'],
        title=f'ウイスキーの{column}のクラスタリング分析',
        opacity=0.7  # 透明度を設定
    )

    # 点のサイズを小さく設定
    fig.update_traces(marker=dict(size=5))

    # HTMLファイルとして出力
    fig.write_html(f"plot_{column.lower()}_clusters.html")

def plot_2d_scatter_scotch_single_malt(df, column, embeddings):
    # スコットランドのシングルモルトウイスキーに限定
    mask = (df['Style'] == 'Single Malt') & (df['Country'] == 'Scotland')
    df_filtered = df[mask].copy()
    embeddings_filtered = embeddings[mask]

    # PCAによる次元削減
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings_filtered)

    # 結果をDataFrameに追加
    df_filtered['x'] = reduced_embeddings[:, 0]
    df_filtered['y'] = reduced_embeddings[:, 1]

    # 2Dプロットの作成
    fig = px.scatter(
        df_filtered,
        x='x',
        y='y',
        color='Region',  # リージョンで色分け
        hover_data=['Title', column, 'Score'],
        title=f'スコットランドシングルモルトウイスキーの{column}の2D可視化',
        opacity=0.7  # 透明度を設定
    )

    # 点のサイズを小さく設定
    fig.update_traces(marker=dict(size=5))

    # HTMLファイルとして出力
    fig.write_html(f"plot_scotch_single_malt_{column.lower()}_2d.html")

if __name__ == "__main__":

    # DataFrameの作成
    df = get_review_data()

    # 数値カラムの変換
    df = convert_numeric_columns(df)

    # ベクトル化されたデータの読み込み
    embedded_dict = get_embedded_dict()

    # 評価項目のリスト
    columns = ['Nose', 'Palate', 'Finish', 'Comment']

    # 各評価項目についてプロットを作成
    for column in columns:
        # ベクトルをnumpy配列に変換
        embeddings = np.array([item[f'{column}_embedding'] for item in embedded_dict])
        #plot_3d_scatter(df, column, embeddings)
        #plot_2d_scatter(df, column, embeddings)
        #plot_2d_scatter_with_clusters(df, column, embeddings)
        plot_2d_scatter_scotch_single_malt(df, column, embeddings)

