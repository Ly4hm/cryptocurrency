from flask import Flask, request, jsonify
import random
from Crypto.PublicKey import RSA
import hashlib

app = Flask(__name__)

# 银行初始化
key = RSA.generate(2048)
n = key.n
e = key.e
d = key.d

# 存储交易信息
transaction_store = {}  # {xi: [(zi, data), ...]}

def H(message):
    return hashlib.sha1(message.encode()).hexdigest()

@app.route('/public_key', methods=['GET'])
def public_key():
    return jsonify({'n': n, 'e': e})

@app.route('/select_indices', methods=['POST'])
def select_indices():
    k = request.json['k']
    indices = list(range(k))
    random.shuffle(indices)
    checked_indices = indices[:k // 2]
    return jsonify({'indices': checked_indices})

@app.route('/verify_and_sign', methods=['POST'])
def verify_and_sign():
    revealed_info = request.json['revealed_info']
    blinded_messages = request.json['blinded_messages']

    # 验证付款人提供的信息
    for info in revealed_info:
        ri, ai, ci, di, xi, yi, S_blind = info
        computed_xi = H(ai + ci)
        if computed_xi != xi:
            return jsonify({'status': 'failed', 'error': 'Invalid xi'}), 400

    # 对未被检查的消息进行签名
    signed_messages = []
    for msg in blinded_messages:
        S = pow(msg, d, n)
        signed_messages.append(S)

    return jsonify({'signed_messages': signed_messages})

@app.route('/verify_transaction', methods=['POST'])
def verify_transaction():
    transactions = request.json['transactions']
    double_spending_detected = False
    u_value = None

    for transaction in transactions:
        zi = transaction['zi']
        data = transaction['data']

        xi = data[0]  # xi 作为交易标识

        if xi in transaction_store:
            # 检查是否有不一致的交易
            for stored_zi, stored_data in transaction_store[xi]:
                if stored_zi != zi:
                    # 检测到双重支付
                    if zi == 0 and stored_zi == 1:
                        xi_1, ai_1, yi_1 = stored_data
                        ai_exp_2 = data[1]
                        u_value = recover_u_from_data(ai_exp_2, ai_1)
                    elif zi == 1 and stored_zi == 0:
                        ai_exp_1 = stored_data[1]
                        ai_2 = data[1]
                        u_value = recover_u_from_data(ai_exp_1, ai_2)
                    else:
                        continue

                    double_spending_detected = True
                    break

            if double_spending_detected:
                break

        # 存储交易
        transaction_store.setdefault(xi, []).append((zi, data))

    if double_spending_detected:
        return jsonify({'status': 'failed', 'error': 'Double spending detected', 'payer_identity': u_value}), 400

    return jsonify({'status': 'success'})

def recover_u_from_data(ai_exp_hex, ai):
    # ai_exp = ai ** (u || (v + i))
    # 因此 (ai_exp ** ai) = u || (v + i)
    ai_bytes = ai.encode('utf-8')
    ai_exp_bytes = bytes.fromhex(ai_exp_hex)

    # 异或恢复 u_v_i
    u_v_i_bytes = bytes(a ^ b for a, b in zip(ai_exp_bytes, ai_bytes))

    # 提取 u（假设 u 的长度为 7）
    u_length = 7
    u_bytes = u_v_i_bytes[:u_length]
    u = u_bytes.decode('utf-8', errors='ignore')
    return u

if __name__ == "__main__":
    app.run(port=5000)
