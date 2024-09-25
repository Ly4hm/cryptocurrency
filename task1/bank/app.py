from flask import Flask, jsonify, request
from bank.server_core import Bank

app = Flask(__name__)

# 初始化 Bank 实例
bank = Bank()


@app.route("/sign_coin", methods=["POST"])
def sign_coin():
    data = request.get_json()
    blinded_coin_without_signature_base64 = data.get("blinded_coin_without_signature_base64")
    userid = data.get("userid")

    if not blinded_coin_without_signature_base64 or not userid:
        return jsonify({"error": "缺少参数"}), 400

    try:
        signature = bank.sign_coin(blinded_coin_without_signature_base64, userid)
        return jsonify({"signature": signature})
    except Exception as e:
        return jsonify({"error": f"出错了: {str(e)}"}), 500


@app.route("/exchange", methods=["POST"])
def exchange():
    data = request.get_json()
    coin = data.get("coin")
    userid = data.get("userid")

    if not coin or not userid:
        return jsonify({"error": "缺少参数"}), 400

    try:
        if bank.exchange(coin, userid):
            return jsonify({"message": "交换成功"})
        else:
            return jsonify({"message": "交换失败"}), 400
    except Exception as e:
        return jsonify({"error": f"出错了: {str(e)}"}), 500


@app.route("/deliver_pubkey", methods=["GET"])
def deliver_pubkey():
    try:
        pubkey = bank.deliver_pub_key()
        return jsonify({"public_key": pubkey})
    except Exception as e:
        return jsonify({"error": f"出错了，原因为 {str(e)}"}), 500


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    password = data.get("password")

    if not password:
        return jsonify({"error": "缺少密码"}), 400

    try:
        userid = bank.register(password)
        return jsonify({"message": "账号注册成功","userid": userid})
    except Exception as e:
        return jsonify({"error": f"出错了: {str(e)}"}), 500


@app.route("/verify_signature", methods=["POST"])
def verify_signature():
    """
    验证货币签名是否有效

    请求体应包含：
    - coin_base64: base64 编码的序列化货币数据
    - signature_base64: base64 编码的签名数据
    """
    data = request.get_json()
    coin_base64 = data.get("coin_base64")
    signature_base64 = data.get("signature_base64")

    if not coin_base64 or not signature_base64:
        return jsonify({"error": "缺少参数"}), 400

    try:
        is_valid = bank.verify_coin_signature(coin_base64, signature_base64)
        if is_valid:
            return jsonify({"valid": True, "message": "签名有效"})
        else:
            return jsonify({"valid": False, "message": "签名无效"}), 400
    except Exception as e:
        return jsonify({"error": f"出错了: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8008)
