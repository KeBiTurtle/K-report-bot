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

# 4. 브리핑 메시지 조립
message = f"""
📊 주식 시장 브리핑 ({today})

🇰🇷 [한국 증시 마감]
- 코스피: {kospi}
- 코스닥: {kosdaq}

🇺🇸 [미국 증시 마감]
- 나스닥: {nasdaq}
- S&P 500: {sp500}
"""

# 5. 텔레그램으로 전송
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {'chat_id': chat_id, 'text': message}
requests.post(url, data=payload)
