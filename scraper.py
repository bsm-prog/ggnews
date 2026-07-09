import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json

def fetch_local_news(region, keywords):
    keyword_query = " OR ".join(keywords)
    search_query = f"{region} ({keyword_query})"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    xml_data = response.read()
    root = ET.fromstring(xml_data)
    news_list = []
    exclude_keywords = ["동정", "인사발령", "부고"]
    for item in root.findall('./channel/item'):
        title = item.find('title').text
        link = item.find('link').text
        pub_date = item.find('pubDate').text
        if any(ex_kw in title for ex_kw in exclude_keywords):
            continue
        news_list.append({"title": title, "link": link, "date": pub_date})
        if len(news_list) >= 10:
            break
    return news_list

# 고양시 기사를 수집합니다.
ISSUE_KEYWORDS = ["지적", "예산", "조례", "민원", "촉구", "대책"]
result_news = fetch_local_news("고양시", ISSUE_KEYWORDS)

# 파일을 저장합니다. (이게 핵심입니다!)
with open("news_data.json", "w", encoding="utf-8") as f:
    json.dump(result_news, f, ensure_ascii=False, indent=4)

print("성공! 'news_data.json' 파일이 생성되었습니다.")