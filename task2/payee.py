from flask import Flask, request, jsonify
import random
import requests

app = Flask(__name__)

bank_url = "http://localhost:5000"

@app.route('/receive_payment', methods=['POST'])
def receive_payment():
    # 从付款人接收电子现金
    payment_data = request.json
    S = payment_data['S']
    payer_url = payment_data['payer_url']
    k = len(S)

    # 生成挑战 zi (0 或 1)
    challenges = [random.randint(0, 1) for _ in range(k)]

    # 向付款人请求响应
    response = requests.post(payer_url + "/respond_to_challenges", json={'challenges': challenges})
    if response.status_code != 200:
        return jsonify({'status': 'failed', 'error': 'Failed to get responses from payer'}), 400

    responses = response.json()['responses']

    # 构建交易数据并提交给银行进行验证
    transactions = [{'zi': z, 'data': data} for z, data in zip(challenges, responses)]
    response = requests.post(bank_url + "/verify_transaction", json={'transactions': transactions})

    if response.status_code == 200 and response.json()['status'] == 'success':
        return jsonify({'status': 'payment accepted'})
    else:
        return jsonify({'status': 'payment failed', 'error': response.json().get('error')}), 400

if __name__ == "__main__":
    app.run(port=5002)
