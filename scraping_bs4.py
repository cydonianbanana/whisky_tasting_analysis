import requests
from bs4 import BeautifulSoup
import json
import ast
import time
import csv

def scrape_whisky_data(url):
    """
    指定されたURLからウイスキーのテイスティングデータをスクレイピングします。

    Args:
        url: スクレイピング対象のURL。

    Returns:
        辞書のリスト。各辞書は1つのレビューに対応し、
        data-review-id, data-nose, data-palate, data-finish, data-comment, data-review-score
        の各データを含む。エラーが発生した場合はNoneを返す。
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
        soup = BeautifulSoup(response.content, "html.parser")

        # ウイスキーの詳細情報を取得
        whisky_details = {}
        details_div = soup.find('div', class_='col-span-2 md:col-span-1 w-full')
        if details_div:
            for p in details_div.find_all('p'):
                strong = p.find('strong')
                if strong:
                    key = strong.text.strip().replace(':', '')
                    value = p.text.replace(strong.text, '').strip()
                    whisky_details[key] = value

        # タイトル情報の取得
        title = soup.find('title').text.split('|')[0].strip()
        
        # レビュー情報の取得
        # data-review-id属性を持つbutton要素を抽出
        review_elements = soup.find_all("button", attrs={"data-review-id": True})
        
        reviews = []
        for review_element in review_elements:
            # レビュー情報とウイスキーの詳細情報を結合
            review = {
                'review-id': review_element.get('data-review-id', '').replace("\\r", " "),
                'title': title,
                # ウイスキーの詳細情報を直接追加
                'Distillery': 'NaN',
                'ABV': whisky_details.get('ABV', ''),
                'Age': whisky_details.get('Age', ''),
                'Style': whisky_details.get('Style', ''),
                'Country': whisky_details.get('Country', ''),
                'Region': whisky_details.get('Region', ''),
                'Bottling': whisky_details.get('Bottling', ''),
                # レビュー情報を追加
                'Score': review_element.get('data-review-score', ''),
                'Nose': review_element.get('data-nose', '').replace("\\r", " "),
                'Palate': review_element.get('data-palate', '').replace("\\r", " "),
                'Finish': review_element.get('data-finish', '').replace("\\r", " "),
                'Comment': review_element.get('data-comment', '').replace("\\r", " "),
                'URL': url,
            }
            reviews.append(review)
        return reviews
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}") #その他のエラーをキャッチ
        return None

def read_urls_from_sitemap(file_path):
    """
    sitemap.outファイルからURLを読み込みます。
    ファイルはPythonリスト形式で記述されていることを想定しています。

    Args:
        file_path: sitemap.outファイルのパス

    Returns:
        URLのリスト
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            # 安全にリストを評価するために、ast.literal_evalを使用
            urls = ast.literal_eval(content)
            if not isinstance(urls, list):
                print(f"エラー: {file_path}の内容がリスト形式ではありません。")
                return []
            return urls
    except FileNotFoundError:
        print(f"エラー: {file_path}が見つかりません。")
        return []
    except SyntaxError:
        print(f"エラー: {file_path}の形式が正しくありません。Pythonリスト形式で記述してください。")
        return []
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました: {e}")
        return []

def find_distillery(title):
    """
    タイトルから蒸留所名を特定します。
    """
    try:
        with open('distilleries_scotland.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Distillery'].lower() in title.lower():
                    return row['Distillery']
    except Exception as e:
        print(f"蒸留所データの読み込み中にエラーが発生しました: {e}")
    return None

if __name__ == "__main__":
    sitemap_path = "sitemap.out"
    urls = read_urls_from_sitemap(sitemap_path)
    
    all_reviews = []  # すべてのレビューを保存するリスト
    
    for url in urls:
        time.sleep(1)
        reviews = scrape_whisky_data(url)
        if reviews:
            for review in reviews:
                # スコットランドのウイスキーの場合、蒸留所名を追加
                if review['Country'] == 'Scotland':
                    distillery = find_distillery(review['title'])
                    if distillery:
                        review['Distillery'] = distillery
                all_reviews.append(review)
        else:
            print(f"スクレイピングに失敗しました: {url}")
    
    # すべてのレビューをJSONファイルに書き込む
    with open('reviews.json', 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, indent=4, ensure_ascii=False)
