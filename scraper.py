import urllib.request
import json
import datetime
import re
import html
import os

# ==========================================
# 1. 환경 설정 및 API 키 (GitHub Secrets에서 가져오기)
# ==========================================
# 🚨 이제 코드에 직접 키를 적지 않습니다! 깃허브 금고에서 안전하게 꺼내옵니다.
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

# 11개 분야 및 핫이슈 사전 (기존과 동일)
CATEGORIES = {
    "기획·재정": ["예산", "결산", "재정", "조세", "세금", "세수", "도정", "감사", "공공기관", "균형발전", "지방채", "교부금", "기금", "납세"],
    "경제·노동": ["일자리", "고용", "노동", "소상공인", "중소기업", "창업", "투자", "지역화폐", "수출", "노조", "플랫폼노동", "비정규직", "상권"],
    "안전·행정": ["소방", "재난", "안전", "치안", "자치행정", "인사", "공무원", "재해", "지진", "수해", "폭우", "폭염", "시민단체", "주민자치"],
    "문화·체육·관광": ["문화", "예술", "체육", "관광", "축제", "도서관", "박물관", "미술관", "체육관", "공연", "유적", "콘텐츠", "체전"],
    "미래과학·협력": ["AI", "인공지능", "R&D", "첨단산업", "반도체", "바이오", "드론", "산학협력", "국제교류", "ODA", "스타트업", "빅데이터"],
    "도시·환경": ["환경", "생태", "기후변화", "탄소중립", "폐기물", "쓰레기", "미세먼지", "수질", "그린벨트", "도시계획", "재개발", "도시재생", "수소"],
    "건설·교통": ["교통", "철도", "지하철", "버스", "도로", "건설", "건축", "GTX", "신도시", "택지", "착공", "대중교통", "주차장", "환승"],
    "보건·복지": ["복지", "보건", "의료", "병원", "장애인", "노인", "어르신", "기초생활수급", "공공의료", "감염병", "요양", "보건소", "취약계층"],
    "농정·해양": ["농업", "어업", "축산", "농민", "농촌", "귀농", "수산물", "해양", "항만", "동물보호", "반려견", "방역", "로컬푸드"],
    "교육(기획/행정)": ["교육청", "교육감", "교육예산", "학교", "학생", "교사", "학부모", "급식", "무상급식", "늘봄", "돌봄", "교권", "학교폭력", "통학로"],
    "여성·가족·평생교육": ["여성", "가족", "보육", "어린이집", "유치원", "저출산", "청년", "평생교육", "성평등", "다문화", "청소년", "아동학대", "1인가구"]
}
HOT_ISSUES = ["지연", "반발", "논란", "예산 부족", "중단", "사고", "촉구", "민원", "특혜", "비판", "우려"]

# 검색 대상 (필요시 시군, 의원명 추가 가능)
TARGET_KEYWORDS = ["경기도의회", "수원시 행정", "고양시 행정", "용인시 행정", "성남시 행정", "하남시 행정", "강성삼", "고은정"]


# ==========================================
# 2. 핵심 로직 함수 (기존과 동일)
# ==========================================
def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text)

def categorize_article(title, content):
    text_to_analyze = title + " " + content
    best_category = "기타"
    max_score = 0
    for category, keywords in CATEGORIES.items():
        score = sum(text_to_analyze.count(kw) for kw in keywords)
        if score > max_score:
            max_score = score
            best_category = category
    return best_category

def check_hot_issue(title, content):
    text_to_analyze = title + " " + content
    for kw in HOT_ISSUES:
        if kw in text_to_analyze:
            return True
    return False

def get_naver_news(keyword):
    if not CLIENT_ID or not CLIENT_SECRET:
        print("API 키가 설정되지 않았습니다.")
        return []
        
    encText = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display=15&sort=date"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    
    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            return json.loads(response.read().decode('utf-8'))['items']
    except Exception as e:
        print(f"[{keyword}] 검색 실패: {e}")
    return []


# ==========================================
# 3. 수집 실행 및 파일 저장
# ==========================================
# 한국 시간(KST) 설정
kst_timezone = datetime.timezone(datetime.timedelta(hours=9))
now_kst = datetime.datetime.now(kst_timezone)

print("자동화 로봇: 데이터 수집을 시작합니다...")
processed_articles = []
seen_links = set()

for keyword in TARGET_KEYWORDS:
    news_items = get_naver_news(keyword)
    for item in news_items:
        link = item['link']
        if link in seen_links:
            continue
        seen_links.add(link)
        
        title = clean_html(item['title'])
        content = clean_html(item['description'])
        
        category = categorize_article(title, content)
        is_hot = check_hot_issue(title, content)
        
        # 기사 발행일 포맷팅
        pub_date = datetime.datetime.strptime(item['pubDate'], "%a, %d %b %Y %H:%M:%S %z")
        formatted_date = pub_date.strftime("%Y-%m-%d")
        
        processed_articles.append({
            "title": title,
            "content": content,
            "municipality": keyword.split()[0],
            "date": formatted_date,
            "url": link,
            "category": category,
            "is_hot_issue": is_hot
        })

# 새로운 데이터를 data.json 에 덮어쓰기
output_data = {
    "last_updated": now_kst.strftime("%Y-%m-%d %H:%M:%S"),
    "articles": processed_articles
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"수집 완료! 총 {len(processed_articles)}개의 기사가 업데이트되었습니다.")
