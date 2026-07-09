import os
from dotenv import load_dotenv
import anthropic

# 1. 아까 만든 .env 파일에서 열쇠(API 키)를 안전하게 꺼내옵니다.
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# 2. 클로드와 연결합니다.
client = anthropic.Anthropic(api_key=api_key)

def generate_report(user_topic, articles_text):
    """
    사용자가 선택한 기사들과 주제를 바탕으로 클로드에게 보고서 작성을 요청합니다.
    """
    
    # 3. 우리의 '최상급 공공행정 전문가 프롬프트'를 심어줍니다.
    prompt = f"""
    당신은 공공기관 정책보고서 작성 전문가입니다. 
    제공된 [보도자료]를 바탕으로 '{user_topic}'에 관한 개조식 보고서를 작성하세요.
    
    [작성 원칙]
    - 4단 구조(Why-What-How-So What)를 지킬 것.
    - 공공기관 공문서 문체를 사용할 것.
    - 이모지를 사용하지 말고, 깔끔하게 정리할 것.
    
    [보도자료 데이터]
    {articles_text}
    """

    # 4. 클로드에게 요청을 보냅니다.
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620", # 가장 뛰어난 모델입니다.
        max_tokens=2000,
        temperature=0.3, # 보고서니까 너무 창의적이지 않고 차분하게 작성하도록 설정
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

# 테스트 실행
if __name__ == "__main__":
    # 나중에 HTML에서 입력받을 데이터들입니다.
    my_topic = "수원시 공공시설 확충 관련 보고"
    my_articles = "1. 수원시, 노후 도서관 리모델링 예산 확보\n2. 수원시, 신규 체육센터 건립 논의"
    
    print("AI가 보고서를 작성 중입니다... 잠시만 기다려주세요.")
    report = generate_report(my_topic, my_articles)
    print("\n--- [생성된 보고서 초안] ---\n")
    print(report)