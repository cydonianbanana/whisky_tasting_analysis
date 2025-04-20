import requests
from bs4 import BeautifulSoup
import json
import ast
import time

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
                'ABV': whisky_details.get('ABV', ''),
                'Age': whisky_details.get('Age', ''),
                'Style': whisky_details.get('Style', ''),
                'Country': whisky_details.get('Country', ''),
                'Region': whisky_details.get('Region', ''),
                'Bottling': whisky_details.get('Bottling', ''),
                # レビュー情報を追加
                'score': review_element.get('data-review-score', ''),
                'nose': review_element.get('data-nose', '').replace("\\r", " "),
                'palate': review_element.get('data-palate', '').replace("\\r", " "),
                'finish': review_element.get('data-finish', '').replace("\\r", " "),
                'comment': review_element.get('data-comment', '').replace("\\r", " "),
                'url': url,
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

if __name__ == "__main__":
    sitemap_path = "sitemap.out"
    urls = read_urls_from_sitemap(sitemap_path)
    
    for url in urls:
        if not urls:
            print("URLが見つかりませんでした。")
            continue
        time.sleep(1)
        scraped_data = scrape_whisky_data(url)
        if scraped_data:
            for i in scraped_data:
                with open('reviews.json', 'w') as f:
                    f.write(json.dumps(i, indent=4))
        else:
            print(f"スクレイピングに失敗しました: {url}")
