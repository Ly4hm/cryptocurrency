import os
from flask import Flask, request, jsonify
import random
from Crypto.PublicKey import RSA
import hashlib
import pickle

app = Flask(__name__)

# 银行初始化
key = RSA.generate(2048)
n = key.n
e = key.e
d = key.d


# 存储交易信息
transaction_store = [] #[(zi,data[]),......]
users = []

if os.path.exists("transaction_store.pickle"):
    transaction_store = pickle.load(open("transaction_store.pickle", "rb"))

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
        if zi == 0:
            #对每个数据异或
            for _,data_stored in transaction_store:
                u_value = recover_u_from_data(data[1], data_stored[0])
                #查找是否有双花者
                if u_value in users:
                    double_spending_detected = True
                    break         
            
        else:
            for _,data_stored in transaction_store:
                u_value = recover_u_from_data(data[0], data_stored[1])
                
                if u_value in users:
                    double_spending_detected = True
                    break


            if double_spending_detected:
                break

        # 交易重复性判别
        if data in transaction_store.values():
            return "交易重复",400

        # 存储交易
        transaction_store.setdefault(xi, []).append((zi, data))
        if transactions["store"]:
            pickle.dump(transaction_store, open("transaction_store.pickle", "wb"))

            
    if double_spending_detected:
        return jsonify({'status': 'failed', 'error': 'Double spending detected', 'payer_identity': u_value}), 400

    #确认无双花之后进行存储
    for transaction in transactions:
        zi = transaction['zi']
        data = transaction['data']
        transaction_store.append((zi, data))

    if transactions["store"]:
        pickle.dump(transaction_store, open("transaction_store.pickle", "wb"))
    
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
