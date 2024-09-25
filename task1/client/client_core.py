import base64
import hashlib
import os
import pickle
import sys

from datetime import datetime

import requests
from cryptography.hazmat.primitives import serialization

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.coin import Coin
from client.utils import BlindingDevice


class Client:
    """用户
    实现操作：
    1. 消息盲化
    2. 签名验证
    3. 货币数据生成
    4. 货币数据查看
    """

    def __init__(self, pub_key_base64: str, userid: str, server_url: str) -> None:
        """
        初始化客户端
        Args:
            pub_key_base64 (str): 服务器分发的公钥，base64 编码的pickle序列化后的pem字节流
            userid (str): 用户ID
            server_url (str): 服务器的URL，例如 "http://localhost:8008"
        """
        # 将序列化后的 pem 字节流还原为 RSAPublicKey 对象
        pub_key_pickle = base64.b64decode(pub_key_base64)
        loaded_pub_key_bytes = pickle.loads(pub_key_pickle)
        self.public_key = serialization.load_pem_public_key(loaded_pub_key_bytes)

        # 盲化器
        self.blind_device = BlindingDevice(self.public_key)

        # 用户ID
        self.userid = userid

        # 服务器URL
        self.server_url = server_url

    def make_coin(self, expiry_date: datetime = None) -> str:
        "生成货币数据"
        # 盲化货币
        coin_without_signature = Coin(expiry_date)
        coin_without_signature_pickle = pickle.dumps(coin_without_signature)
        blinded_coin = self.blind_device.blind_message(coin_without_signature_pickle)

        # 签名
        blinded_signature = self.get_signature(blinded_coin)
        signature = self.blind_device.unblind_signature(blinded_signature)

        coin_with_signature = "{}:{}".format(
            base64.b64encode(coin_without_signature_pickle).decode("utf-8"),
            base64.b64encode(signature).decode("utf-8"),
        )

        return coin_with_signature

    def get_signature(self, blinded_coin: bytes) -> bytes:
        "获取签名, 返回signature的base64解码后字节流"
        try:
            url = f"{self.server_url}/sign_coin"
            payload = {
                "blinded_coin_without_signature_base64": base64.b64encode(blinded_coin).decode("utf-8"),
                "userid": self.userid
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                signature_base64 = data.get("signature")
                if not signature_base64:
                    raise Exception("签名数据缺失")
                return base64.b64decode(signature_base64)
            else:
                error_msg = response.json().get("error", "未知错误")
                raise Exception(f"获取签名失败: {error_msg}")
        except Exception as e:
            print(f"获取签名时出错: {e}")
            raise

    def view_coin(self, coin_b: str) -> tuple:
        "解析 base64 编码后的 coin 字节流"
        coin = pickle.loads(base64.b64decode(coin_b))
        return coin.uid, coin.expiry_date

    def verify_coin(self, coin: str) -> bool:
        """验证货币
        此处 coin 格式为 make_coin 方法生成的字符串格式"""
        # 检查coin格式
        if ":" not in coin:
            print("Coin格式错误: 缺少 ':' 分隔符")
            return False

        parts = coin.split(":")
        if len(parts) != 2:
            print("Coin格式错误: 分隔符数量不正确")
            return False

        coin_pickle_b64, signature_b64 = parts

        # 校验base64编码
        try:
            coin_pickle = base64.b64decode(coin_pickle_b64)
            signature = base64.b64decode(signature_b64)
        except Exception as e:
            print(f"Base64解码失败: {e}")
            return False

        # 校验货币数据结构
        try:
            coin_obj = pickle.loads(coin_pickle)
            if not isinstance(coin_obj, Coin):
                print("Coin数据格式错误")
                return False
        except Exception as e:
            print(f"反序列化Coin时出错: {e}")
            return False

        if coin_obj.expiry_date:
            if datetime.utcnow() > coin_obj.expiry_date:
                print("Coin已过期")
                return False

        try:
            public_numbers = self.public_key.public_numbers()
            e = public_numbers.e
            n = public_numbers.n

            s_int = int.from_bytes(signature, byteorder="big")

            # 计算 m' = (s_int)^e mod n
            m_prime_int = pow(s_int, e, n)

            message_hash = hashlib.sha256(coin_pickle).digest()
            m_int = int.from_bytes(message_hash, byteorder="big")

            if m_prime_int == m_int:
                print("签名有效")
                return True
            else:
                print("签名无效")
                return False
        except Exception as e:
            print(f"验证签名时出错: {e}")
            return False

#
# if __name__ == "__main__":
#     client = Client(
#         "gASVygEAAAAAAABCwwEAAC0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBc0orWXJNaXlrZ1laRkg2ejJ0WmoKTS9OYlNlNWZ1cW8xZmpGNWdXTCtPY3licGdibjN5cG1JQTFlbDV3ZkdRN2p3anhUVEhhSWhqNUFnVWt6RGxnNwplY3gxRHJmNU9qY3Q0UjlMdDd2VWZQOHE2eVZMVm1UanhSMFgxTmJsQm5mZ3UwWjZHTjVvTVBMNjZiQnAwOVpzCjB3QzRGQ2JydlV3STZSTVozVnNiR1ptY2lEUjFSQ0hKNStrazZNdGFtbS91TEdoSWRjT0ZjdFZqNTV4LzNtcjkKK3JFbHNkd1gzQm82V00xMm10U3k0UWZPeFVLTmlVOFdYUXBLVXhtWHNyaENPd1ZJOHQ4MkcrcTJsamtLOUgxaworWm41akdkcXJyalNMZHlWRTMwVVo3VjgrTk1neHFhaFhYdDdWdnhMYldDRmgrNmp0NkdoZ3h3cENvYmJrY1M2Cmx3SURBUUFCCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQqULg=="
#     )
#     coin = client.make_coin()
#
#     print(coin)
#     print(client.view_coin(coin))