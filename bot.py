import requests
import FinanceDataReader as fdr
from pykrx import stock
from datetime import datetime, timedelta

# 1. 텔레그램 설정
bot_token = "8884687082:AAEYg_SXp40-QQPIxQGGcBkrltaXPCMjims"
chat_id = "7495180649"

# 2. 날짜 설정 (가장 최근 평일 찾기)
today = datetime.today()
if today.weekday() == 5:  # 토요일
    target_date = today - timedelta(days=1)
elif today.weekday() == 6:  # 일요일 (오늘)
    target_date = today - timedelta(days=2)
else:
    target_date = today

fdr_date = target_date.strftime('%Y-%m-%d') # 예: 2026-07-31
krx_date = target_date.strftime('%Y%m%d')   # 예: 20260731

# 3. 주식 지수 가져오기
def get_index_close(ticker, date_str):
    try:
        df = fdr.DataReader(ticker, date_str)
        if not df.empty:
            return round(df['Close'].iloc[-1], 2)
        else:
            return "데이터 없음"
    except Exception as e:
        return f"오류: {e}"

kospi = get_index_close('KS11', fdr_date)
kosdaq = get_index_close('KQ11', fdr_date)
nasdaq = get_index_close('IXIC', fdr_date)
sp500 = get_index_close('US500', fdr_date)

# 4. 수급 데이터 가져오기 (가장 안정적인 함수 사용)
def get_trading_volume(ticker, date_str):
    try:
        # 이 함수는 해당 일자의 종목별 투자자 순매수 '거래량'을 데이터프레임으로 반환합니다.
        # 인덱스가 투자자(개인, 외국인, 기관합계 등)로 되어 있습니다.
        df = stock.get_market_net_purchases_of_equities_by_investor(date_str, date_str, "KOSPI", ticker)
        
        if not df.empty:
            # 인덱스(투자자명)를 기준으로 '순매수거래량' 값을 가져옵니다.
            # 만약 해당 투자자 데이터가 없으면 0으로 처리합니다.
            retail = df.loc['개인', '순매수거래량'] if '개인' in df.index else 0
            inst = df.loc['기관합계', '순매수거래량'] if '기관합계' in df.index else 0
            foreigner = df.loc['외국인', '순매수거래량'] if '외국인' in df.index else 0
            
            # 가독성을 위해 만 단위(천 단위 콤마)로 표시하거나 직관적인 숫자로 포맷팅합니다.
            return f"개인: {retail:,}주 | 기관: {inst:,}주 | 외인: {foreigner:,}주"
        else:
            return "수급 데이터 없음"
    except Exception as e:
         # 에러 발생 시 어떤 에러인지 텔레그램으로 받아볼 수 있게 합니다.
        return f"에러: {e}"

samsung_vol = get_trading_volume("005930", krx_date)
hynix_vol = get_trading_volume("000660", krx_date)

# 5. 브리핑 메시지 조립
message = f"""
📊 주식 시장 브리핑 (기준일: {fdr_date})

🇰🇷 [한국 증시 마감]
- 코스피: {kospi}
- 코스닥: {kosdaq}

🇺🇸 [미국 증시 마감]
- 나스닥: {nasdaq}
- S&P 500: {sp500}

🏢 [주요 종목 순매수 수급 (단위: 주)]
- 삼성전자: {samsung_vol}
- SK하이닉스: {hynix_vol}
"""

# 6. 텔레그램으로 전송
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {'chat_id': chat_id, 'text': message}
requests.post(url, data=payload)
