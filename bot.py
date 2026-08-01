import requests

# 아래 본인의 토큰과 Chat ID로 수정하세요
bot_token = "8884687082:AAEYg_SXp40-QQPIxQGGcBkrltaXPCMjims" 
chat_id = "7495180649"

message = "국장/미장 브리핑 테스트입니다! 컴퓨터 없이 스마트폰으로 세팅 완료!"

url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
requests.get(url)
