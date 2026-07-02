import json
import datetime
import re

# ==========================================
# 1. 환경 설정 및 사전(Dictionary) 세팅
# ==========================================

# 우리가 기획한 11개 분야 핵심 키워드 사전
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

# 행정사무감사용 핫이슈 탐지 키워드 (토글 ON 시 작동할 기준)
HOT_ISSUES = ["지연", "반발", "논란", "예산 부족", "중단", "사고", "촉구", "민원", "특혜", "비판", "우려"]


# ==========================================
# 2. 핵심 로직 함수 (점수제 분류 및 핫이슈 판별)
# ==========================================

def categorize_article(title, content):
    """제목과 본문을 분석하여 가장 점수가 높은 1개 분야를 반환합니다."""
    text_to_analyze = title + " " + content
    best_category = "기타"
    max_score = 0
    
    for category, keywords in CATEGORIES.items():
        # 해당 분야의 키워드가 텍스트에 몇 번 등장하는지 합산 (점수 계산)
        score = sum(text_to_analyze.count(kw) for kw in keywords)
        
        if score > max_score:
            max_score = score
            best_category = category
            
    # 매칭된 키워드가 없으면 기본값 '기타' 유지
    return best_category

def check_hot_issue(title, content):
    """텍스트 내에 핫이슈 키워드가 하나라도 있으면 True(🚨)를 반환합니다."""
    text_to_analyze = title + " " + content
    for kw in HOT_ISSUES:
        if kw in text_to_analyze:
            return True
    return False


# ==========================================
# 3. 데이터 수집 및 저장 실행 (샘플 데이터 생성)
# ==========================================
# 실제 웹 크롤링 코드가 들어갈 자리입니다. 
# 지금은 엔진이 어떻게 작동하는지 보기 위해 가상의 보도자료(수원시, 하남시 등) 데이터를 넣습니다.

sample_crawled_data = [
    {
        "title": "하남시, 지하철 연장 공사 예산 부족으로 6개월 지연 불가피",
        "content": "하남시의 핵심 교통망 확충 사업인 지하철 연장 공사가 예산 부족 문제로 인해 착공이 지연되고 있어 시민들의 반발이 예상된다.",
        "municipality": "하남시",
        "date": "2026-07-02",
        "url": "https://example.com/news/1"
    },
    {
        "title": "수원시, 친환경 학교 무상급식 예산 대폭 확대 편성",
        "content": "수원시는 관내 학생들의 건강을 위해 학교 급식 예산을 늘리고 지역 농산물을 활용한 식단을 제공할 계획이다.",
        "municipality": "수원시",
        "date": "2026-07-01",
        "url": "https://example.com/news/2"
    },
    {
        "title": "강성삼 의원, '소상공인 지역화폐 지원 조례안' 발의",
        "content": "강성삼 의원은 골목상권 활성화와 일자리 창출을 위해 소상공인 지역화폐 지원 조례안을 통과시켰다.",
        "municipality": "경기도의회",
        "date": "2026-06-30",
        "url": "https://example.com/news/3"
    }
]

# 수집한 기사에 분야(Category)와 핫이슈(Is_Hot) 태그 달기
processed_articles = []
for article in sample_crawled_data:
    category = categorize_article(article['title'], article['content'])
    is_hot = check_hot_issue(article['title'], article['content'])
    
    article['category'] = category
    article['is_hot_issue'] = is_hot
    processed_articles.append(article)

# 결과를 화면(index.html)이 읽을 수 있게 data.json 파일로 저장
output_data = {
    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "articles": processed_articles
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("성공적으로 뉴스를 수집하고 data.json 파일을 생성했습니다!")
