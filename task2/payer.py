from flask import Flask, request, jsonify
import requests
import hashlib
import random

app = Flask(__name__)

bank_url = "http://localhost:5000"
k = 10
e, n = None, None  # 从银行获取
r_i, a_i, c_i, d_i, x_i, y_i, S_blind, S = [], [], [], [], [], [], [], []
u = 'User123'  # 付款人身份
v = random.randint(1, 100000)  # 计数器

def H(message):
    return hashlib.sha1(message.encode()).hexdigest()

def xor_strings(s1, s2):
    # 确保字符串长度一致
    max_len = max(len(s1), len(s2))
    s1 = s1.ljust(max_len, '\0')
    s2 = s2.ljust(max_len, '\0')
    return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2))

def random_string(length=16):
    import string
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    global e, n
    # 从银行获取公钥
    if not e or not n:
        response = requests.get(bank_url + "/public_key")
        e, n = response.json()['e'], response.json()['n']

    for i in range(k):
        r = random.randint(1, n - 1)
        a = random_string()
        c = random_string()
        d = random_string()
        xi = H(a + c)
        uid_v_i = u + str(v + i)  # u || (v + i)
        y = H(xor_strings(a, uid_v_i) + d)
        H_xy = H(xi + y)
        S_blind_value = (pow(r, e, n) * int(H_xy, 16)) % n
        r_i.append(r)
        a_i.append(a)
        c_i.append(c)
        d_i.append(d)
        x_i.append(xi)
        y_i.append(y)
        S_blind.append(S_blind_value)

    # 发送盲化签名请求给银行
    response = requests.post(bank_url + "/select_indices", json={'k': k})
    checked_indices = response.json()['indices']

    # 返回对应的 ri, ai, ci, di
    revealed_info = []
    for i in checked_indices:
        info = [r_i[i], a_i[i], c_i[i], d_i[i], x_i[i], y_i[i], S_blind[i]]
        revealed_info.append(info)

    # 发送验证信息并获取签名消息
    unchecked_indices = [i for i in range(k) if i not in checked_indices]
    unchecked_blinded_messages = [S_blind[i] for i in unchecked_indices]

    response = requests.post(bank_url + "/verify_and_sign", json={
        'revealed_info': revealed_info,
        'blinded_messages': unchecked_blinded_messages
    })

    if response.status_code != 200:
        return jsonify({'status': 'failed', 'error': response.json().get('error')}), 400

    signed_messages = response.json()['signed_messages']

    # 去盲化签名
    for idx, S_signed in zip(unchecked_indices, signed_messages):
        S_unblinded = (S_signed * pow(r_i[idx], -1, n)) % n
        S.append(S_unblinded)

    return jsonify({'status': 'withdraw successful', 'S': S})

@app.route('/respond_to_challenges', methods=['POST'])
def respond_to_challenges():
    challenges = request.json['challenges']
    responses = []

    for i, zi in enumerate(challenges):
        idx = i % len(x_i)  # 确保索引不越界
        if zi == 1:
            response = [x_i[idx], a_i[idx], y_i[idx]]
        else:
            uid_v_i = u + str(v + idx)
            ai_exp = xor_strings(a_i[idx], uid_v_i)
            ai_exp_hex = ai_exp.encode('utf-8').hex()
            response = [x_i[idx], ai_exp_hex, d_i[idx]]
        responses.append(response)

    return jsonify({'responses': responses})

@app.route('/spend', methods=['POST'])
def spend():
    payee_url = request.json['payee_url']
    # 向收款人发送 S 和付款人 URL
    payment_data = {
        'S': S,
        'payer_url': 'http://localhost:5001'
    }
    response = requests.post(payee_url + '/receive_payment', json=payment_data)
    return response.json()

if __name__ == "__main__":
    app.run(port=5001)
