import base64
from flask import Flask, request, jsonify, render_template
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import hashlib
import os

from utils import SignatureMachine

app = Flask(__name__)

accounts = {
    "buyer1": {"balance": 100, "private_key": None, "public_key": None},
    "buyer2": {"balance": 150, "private_key": None, "public_key": None},
    "seller1": {"balance": 200, "private_key": None, "public_key": None},
}

signature_machine = SignatureMachine()

@app.route('/')
def index():
    return render_template('index.html')


# 买家首先生成盲化的消息并发送给银行
@app.route('/request_signature', methods=['POST'])
def request_signature():
    data = request.json
    buyer = data['buyer']
    seller = data['seller']
    amount = data['amount']

    # 生成交易消息
    message = f"{buyer}支付给{seller}{amount}元".encode('utf-8')

    # 买家盲化消息
    blinded_message = signature_machine.blind_message(message)

    # 将盲化后的消息发送给银行进行签名
    return jsonify({"blinded_message": blinded_message.hex()})


# 银行对盲化后的消息进行签名，并返回给买家
@app.route('/sign_blinded_message', methods=['POST'])
def sign_blinded_message():
    data = request.json
    blinded_message = bytes.fromhex(data['blinded_message'])

    # 银行对盲化消息进行签名
    blinded_signature = signature_machine.sign_message_without_blind(blinded_message)
    # 将盲签名返回给买家
    return jsonify({"blinded_signature": blinded_signature.hex()})


# 买家收到银行的盲签名后，进行去盲化操作并验证签名
@app.route('/verify_transaction', methods=['POST'])
def verify_transaction():
    data = request.json
    buyer = data['buyer']
    seller = data['seller']
    amount = int(data['amount'])
    blinded_signature = bytes.fromhex(data['blinded_signature'])

    # 买家去盲化签名
    signature = signature_machine.unblind_signature(blinded_signature)

    # 原始消息
    message = f"{buyer}支付给{seller}{amount}元".encode('utf-8')

    print("Original message:", message)
    print("Blinded signature (before unblinding):", blinded_signature)
    print("Unblinded signature:", signature)

    # 验证签名
    is_valid = signature_machine.verify_signature(message, signature)

    if is_valid:
        accounts[buyer]['balance'] -= amount
        accounts[seller]['balance'] += amount
        return jsonify({"status": "success", "message": "Transaction completed", "buyer_balance": accounts[buyer]['balance'], "seller_balance": accounts[seller]['balance']})
    else:
        return jsonify({"status": "error", "message": "Signature verification failed"}), 400


@app.route('/check_balance', methods=['GET'])
def check_balance():
    account = request.args.get('account')
    if account in accounts:
        return jsonify({"account": account, "balance": accounts[account]['balance']})
    else:
        return jsonify({"status": "error", "message": "Account not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
#     signature_machine = SignatureMachine()
#     message = "hello world"
#     message_signed = signature_machine.sign(message)
#
#     print(message_signed)
#
#     print(signature_machine.verify(message_signed))
