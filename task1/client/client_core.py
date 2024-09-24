import base64
import hashlib
import os
import pickle
import sys

from datetime import datetime
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

    def __init__(self, pub_key_base64) -> None:
        # 将序列化后的 pem 字节流还原为 RSAPublicKey 对象
        pub_key_pickle = base64.b64decode(pub_key_base64)
        loaded_pub_key_bytes = pickle.loads(pub_key_pickle)
        self.public_key = serialization.load_pem_public_key(loaded_pub_key_bytes)

        # 盲化器
        self.blind_device = BlindingDevice(self.public_key)

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
        # TODO: 向server_core获取签名, 通信通过 http/https 实现
        pass

    def view_coin(self, coin_b: str) -> tuple:
        "解析 base64 编码后的 coin 字节流"
        coin = pickle.loads(base64.b64decode(coin_b))
        return (coin.uid, coin.expiry_date)

    def verify_coin(self, coin: str) -> bool:
        """验证货币
        此处 coin 格式为 make_coin 方法生成的字符串格式"""
        # TODO: 添加对 coin 格式的校验
        # TODO: 添加对 coin 有效期的校验
        # 从字符串格式的 coin 中提取数据
        coin_pickle, signature = coin.split(":")
        coin_pickle = base64.b64decode(coin_pickle)
        signature = base64.b64decode(signature)
        
        # 使用公钥验证签名
        public_numbers = self.public_key.public_numbers()
        e = public_numbers.e
        n = public_numbers.n

        s_int = int.from_bytes(signature, byteorder="big")

        # 计算 m' = (s_int)^e mod n
        m_prime_int = pow(s_int, e, n)

        message_hash = hashlib.sha256(coin_pickle).digest()
        m_int = int.from_bytes(message_hash, byteorder="big")

        return m_prime_int == m_int


if __name__ == "__main__":
    client = Client(
        "gASVygEAAAAAAABCwwEAAC0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBc0orWXJNaXlrZ1laRkg2ejJ0WmoKTS9OYlNlNWZ1cW8xZmpGNWdXTCtPY3licGdibjN5cG1JQTFlbDV3ZkdRN2p3anhUVEhhSWhqNUFnVWt6RGxnNwplY3gxRHJmNU9qY3Q0UjlMdDd2VWZQOHE2eVZMVm1UanhSMFgxTmJsQm5mZ3UwWjZHTjVvTVBMNjZiQnAwOVpzCjB3QzRGQ2JydlV3STZSTVozVnNiR1ptY2lEUjFSQ0hKNStrazZNdGFtbS91TEdoSWRjT0ZjdFZqNTV4LzNtcjkKK3JFbHNkd1gzQm82V00xMm10U3k0UWZPeFVLTmlVOFdYUXBLVXhtWHNyaENPd1ZJOHQ4MkcrcTJsamtLOUgxaworWm41akdkcXJyalNMZHlWRTMwVVo3VjgrTk1neHFhaFhYdDdWdnhMYldDRmgrNmp0NkdoZ3h3cENvYmJrY1M2Cmx3SURBUUFCCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQqULg=="
    )
    coin = client.make_coin()

    print(coin)
    print(client.view_coin(coin))
