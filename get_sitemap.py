from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-96339d37e5894abd9f19e83d55378dc3")

# Map a website:
map_result = app.map_url('https://whiskymag.com/tastings/')

# URLを配列としてsitemap.outに出力
with open('sitemap.out', 'w') as f:
    f.write(str(map_result['links']))
