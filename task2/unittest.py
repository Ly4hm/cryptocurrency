import requests

def test_withdraw():
    response = requests.post('http://localhost:5001/withdraw')
    if response.status_code == 200:
        print("Withdraw test successful:", response.json())
    else:
        print("Withdraw test failed:", response.json())

def test_spend():
    spend_data = {
        'payee_url': 'http://localhost:5002'  # 这里需要一个模拟的收款人服务（可能是另一个FlaskApp）
    }
    response = requests.post('http://localhost:5001/spend', json=spend_data)
    if response.status_code == 200:
        print("Spend test successful:", response.json())
    else:
        print("Spend test failed:", response.json())

test_withdraw()
test_spend() 