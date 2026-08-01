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

# 4. 수급 데이터 가져오기 (호환성 높은 기본 함수 사용)
def get_trading_volume(ticker, date_str):
    try:
        # 지정된 기간(하루) 동안의 투자자별 거래실적 조회
        # 결과: 인덱스가 투자자명(개인, 기관합계, 외국인 등)인 데이터프레임
        df = stock.get_market_trading_volume_by_investor(date_str, date_str, ticker)
        
        if not df.empty:
            # 데이터프레임의 인덱스(투자자명)를 확인하여 '순매수' 컬럼의 값을 가져옴
            # 버전 문제로 '순매수'라는 컬럼명이 다를 수 있으므로, 세 번째 컬럼(iloc[:, 2] - 보통 순매수)을 강제로 가져오는 방법을 씁니다.
            
            # 안전한 추출을 위한 함수 내장
            def get_net_buy(investor_name):
                if investor_name in df.index:
                    # 통상적으로 매도(0), 매수(1), 순매수(2) 순서로 컬럼이 배치됨
                    return df.loc[investor_name].iloc[2] 
                return 0

            retail = get_net_buy('개인')
            inst = get_net_buy('기관합계')
            foreigner = get_net_buy('외국인')
            
            return f"개인: {int(retail):,}주 | 기관: {int(inst):,}주 | 외인: {int(foreigner):,}주"
        else:
            return "수급 데이터 없음"
    except Exception as e:
        return f"에러: {e}"
        
samsung_vol = get_trading_volume("005930", krx_date)
hynix_vol = get_trading_volume("000660", krx_date)
