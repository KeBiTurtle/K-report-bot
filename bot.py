import requests
import FinanceDataReader as fdr
from pykrx import stock
from datetime import datetime, timedelta

# 1. 텔레그램 설정 (본인 정보 유지)
bot_token = "여기에_API_토큰을_넣으세요"
chat_id = "여기에_Chat_ID를_넣으세요"

# 2. 날짜 계산 (주말이면 금요일 날짜로 변경)
today = datetime.today()
if today.weekday() == 5:  # 토요일이면
    target_date = today - timedelta(days=1)
elif today.weekday() == 6:  # 일요일이면
    target_date = today - timedelta(days=2)
else:
    target_date = today

# fdr용 날짜 포맷 (YYYY-MM-DD), pykrx용 날짜 포맷 (YYYYMMDD)
fdr_date = target_date.strftime('%Y-%m-%d')
krx_date = target_date.strftime('%Y%m%d')

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

# 4. 수급 데이터 가져오기 (pykrx 함수 변경)
def get_trading_volume(ticker, date_str):
    try:
        # 순매수 대금 함수 사용 (단위가 직관적임)
        # 인자: 시작일, 종료일, 시장(KOSPI), 투자자(전체 조회는 별도 처리 필요)
        
        # 보다 직관적이고 오류가 적은 종목별 외국인/기관 합산 데이터 조회로 변경
        df = stock.get_market_trading_volume_by_investor(date_str, date_str, ticker)
        
        if not df.empty:
            # 최신 pykrx 버전에 맞춘 데이터 추출 방식 (iloc 활용)
            # 첫 번째 행(해당 날짜)의 개인(0), 기관합계(2), 외국인(5) 컬럼 인덱스 접근 
            # (주의: 컬럼 순서는 pykrx 버전에 따라 다를 수 있어 인덱스 이름으로 접근하는 것이 안전)
            
            # 투자자 이름을 인덱스로 사용하여 안전하게 접근
            retail = df.loc[date_str, '개인'] if '개인' in df.columns else df.iloc[0, 0]
            inst = df.loc[date_str, '기관합계'] if '기관합계' in df.columns else df.iloc[0, 2]
            foreigner = df.loc[date_str, '외국인'] if '외국인' in df.columns else df.iloc[0, 5]
            
            return f"개인: {int(retail):,}주 | 기관: {int(inst):,}주 | 외인: {int(foreigner):,}주"
        else:
            return "수급 데이터 없음"
    except Exception as e:
        return f"오류 발생"

samsung_vol = get_trading_volume("005930", krx_date)
hynix_vol = get_trading_volume("000660", krx_date)

# 5. 메시지 조립
message = f"""
📊 주식 시장 브리핑 (기준일: {fdr_date})

🇰🇷 [한국 증시 마감]
- 코스피: {kospi}
- 코스닥: {kosdaq}

🇺🇸 [미국 증시 마감]
- 나스닥: {nasdaq}
- S&P 500: {sp500}

🏢 [주요 종목 수급 (단위: 주)]
- 삼성전자: {samsung_vol}
- SK하이닉스: {hynix_vol}
"""

# 6. 전송
url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {'chat_id': chat_id, 'text': message}
requests.post(url, data=payload)
