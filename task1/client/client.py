import base64
import os
import pickle
import sys

from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.coin import Coin

class Client:
    """用户
    实现操作：
    1. 消息盲化
    2. 签名验证
    3. 货币数据生成
    4. 货币数据查看
    """

    def __init__(self) -> None:
        pass

    def make_coin(self, expiry_date: datetime = None) -> str:
        "生成货币数据"
        c = Coin(expiry_date)
        return base64.b64encode(pickle.dumps(c)).decode("utf-8")
    
    def view_coin(self, coin_b: str) -> tuple:
        "解析 base64 编码后的 coin 字节流"
        coin = pickle.loads(base64.b64decode(coin_b))
        return (coin.uid, coin.expiry_date)


if __name__ == "__main__":
    client = Client()
    coin = client.make_coin()
    
    print(coin)
    print(client.view_coin(coin))
