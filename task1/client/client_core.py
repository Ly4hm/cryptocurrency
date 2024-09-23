import base64
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

    def make_coin(self, expiry_date: datetime = None) -> str:
        "生成货币数据"
        coin_without_signature = Coin(expiry_date)
        # TODO: 结合server_core

        coin = coin_without_signature

        return base64.b64encode(pickle.dumps(coin)).decode("utf-8")
    
    def get_signature(self, blinded_coin_without_signature_base64:str) -> bytes:
        "获取签名"
        # TODO: 获取签名
        pass

    def view_coin(self, coin_b: str) -> tuple:
        "解析 base64 编码后的 coin 字节流"
        coin = pickle.loads(base64.b64decode(coin_b))
        return (coin.uid, coin.expiry_date)

    def blind_coin(self, public_key):
        "盲化货币"
        # TODO: 盲化货币
        pass

    def verify_coin(self, coin: str) -> bool:
        "验证货币"
        # TODO: 验证货币
        pass

if __name__ == "__main__":
    client = Client(
        "gASVygEAAAAAAABCwwEAAC0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBc0orWXJNaXlrZ1laRkg2ejJ0WmoKTS9OYlNlNWZ1cW8xZmpGNWdXTCtPY3licGdibjN5cG1JQTFlbDV3ZkdRN2p3anhUVEhhSWhqNUFnVWt6RGxnNwplY3gxRHJmNU9qY3Q0UjlMdDd2VWZQOHE2eVZMVm1UanhSMFgxTmJsQm5mZ3UwWjZHTjVvTVBMNjZiQnAwOVpzCjB3QzRGQ2JydlV3STZSTVozVnNiR1ptY2lEUjFSQ0hKNStrazZNdGFtbS91TEdoSWRjT0ZjdFZqNTV4LzNtcjkKK3JFbHNkd1gzQm82V00xMm10U3k0UWZPeFVLTmlVOFdYUXBLVXhtWHNyaENPd1ZJOHQ4MkcrcTJsamtLOUgxaworWm41akdkcXJyalNMZHlWRTMwVVo3VjgrTk1neHFhaFhYdDdWdnhMYldDRmgrNmp0NkdoZ3h3cENvYmJrY1M2Cmx3SURBUUFCCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQqULg=="
    )
    coin = client.make_coin()

    print(coin)
    print(client.view_coin(coin))
