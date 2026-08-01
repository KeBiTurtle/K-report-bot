import requests
import FinanceDataReader as fdr
from datetime import datetime

# 1. 텔레그램 설정
bot_token = "8884687082:AAEYg_SXp40-QQPIxQGGcBkrltaXPCMjims" 
chat_id = "7495180649"

# 2. 오늘 날짜 확인
today = datetime.today().strftime('%Y-%m-%d')

# 3. 주식 지수 데이터 가져오기 (FinanceDataReader 사용)
# KS11(코스피), KQ11(코스닥), IXIC(나스닥), US500(S&P500)
def get_index_close(ticker):
    try:
        # 오늘 날짜 기준으로 최근 데이터를 가져와서 마지막 종가(Close)를 추출
        df = fdr.DataReader(ticker, today)
        if not df.empty:
            return round(df['Close'].iloc[-1], 2)
        else:
            return "데이터 없음"
    except Exception as e:
        return f"오류: {e}"

kospi = get_index_close('KS11')
kosdaq = get_index_close('KQ11')
nasdaq = get_index_close('IXIC')
sp500 = get_index_close('US500')

from pykrx import stock

# --- (여기까지가 기존의 1, 2, 3번 코드입니다) ---

# 4. 삼성전자(005930), SK하이닉스(000660) 수급 데이터 가져오기
def get_trading_volume(ticker, date):
    try:
        # 해당 날짜의 투자자별 순매수 데이터 조회 (단위: 주)
        df = stock.get_market_trading_volume_by_investor(date, date, ticker)
        
        if not df.empty:
            # 개인, 기관합계, 외국인 데이터 추출
            # pykrx 데이터프레임 구조에 맞춰 컬럼 인덱싱
            retail = df.loc[date, '개인']
            inst = df.loc[date, '기관합계']
            foreigner = df.loc[date, '외국인']
            
            # 천 단위 콤마 추가하여 보기 좋게 포맷팅
            return f"개인: {retail:,}주 | 기관: {inst:,}주 | 외인: {foreigner:,}주"
        else:
            return "수급 데이터 없음 (휴일 등)"
    except Exception as e:
        return f"오류: {e}"

# 주의: 오늘이 주말이거나 장 마감 전이면 데이터가 없을 수 있습니다. 
# 확실한 테스트를 위해 가장 최근 평일 날짜(예: '20260731')로 임시 변경해 봅니다.
test_date = '20260731' # 금요일
samsung_vol = get_trading_volume("005930", test_date)
hynix_vol = get_trading_volume("000660", test_date)

# 5. 브리핑 메시지 조립 (수급 정보 추가)
message = f"""
📊 주식 시장 브리핑 ({today})

🇰🇷 [한국 증시 마감]
- 코스피: {kospi}
- 코스닥: {kosdaq}

🇺🇸 [미국 증시 마감]
- 나스닥: {nasdaq}
- S&P 500: {sp500}

🏢 [주요 종목 수급 동향 (기준일: {test_date})]
- 삼성전자: {samsung_vol}
- SK하이닉스: {hynix_vol}
"""

# 6. 텔레그램으로 전송
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {'chat_id': chat_id, 'text': message}
requests.post(url, data=payload)
