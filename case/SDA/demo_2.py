import requests






url = "http://192.168.1.123:10002/dididu/SetStockPrice.do?stockPrice=值&stockId=值"
url_123="http://192.168.1.123:10002/dididu/SetStockPrice.do",

param = {
    "stockPrice": 18.11,
    "stockId": "momo",
}
resp = requests.post(url="http://192.168.1.50:88/dididu/SetStockPrice.do", data=param)
print(resp.status_code)
print(resp.json())