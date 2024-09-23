import base64
import os
import pickle
import sqlite3
import sys

from datetime import datetime
from typing import Any
from cryptography.hazmat.primitives import serialization

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.coin import Coin
from model.user import User
from bank.utils import SignatureMachine


class DataMap:
    "中央银行数据管理类"

    def __init__(self, database: str) -> None:
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

        # 数据库初始化
        self.cursor.execute(
            """
CREATE TABLE IF NOT EXISTS Currency (
    uid TEXT PRIMARY KEY,
    owner TEXT NOT NULL
)
"""
        )
        self.conn.commit()

    def __reduce__(self) -> str | tuple[Any, ...]:
        "垃圾处理"
        self.conn.close()
        self.cursor.close()

    def print_money() -> str:
        "印钞"


class Bank:
    """中央银行"""

    def __init__(self) -> None:
        self.signature_machine = SignatureMachine()

    def sign_coin(self, blinded_coin_without_signature_base64: str) -> str:
        """
        将 coin 数据签名

        coin_without_signature_base64 数据为 pickle 序列化后经过 base64 编码 Currency 数据,然后经过盲化

        Return: 签名的 base64 编码
        """
        blinded_coin_without_signature: bytes = base64.b64decode(
            blinded_coin_without_signature_base64
        )
        blinded_signature = self.signature_machine.sign_message(blinded_coin_without_signature)
        
        return base64.b64encode(blinded_signature).decode("utf-8")

    def deliver_pub_key(self):
        """分发公钥"""
        # 由于 RSAPublicKey 类是不可反序列化的，所以先将其转化为 pem 格式字节串
        pub_key_bytes = self.signature_machine.get_pub_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        pub_key_pickle = pickle.dumps(pub_key_bytes)
        return base64.b64encode(pub_key_pickle).decode("utf-8")


if __name__ == "__main__":
    b = Bank()
    print(
        b.sign_coin(
            "gASVcgAAAAAAAACMCm1vZGVsLmNvaW6UjARDb2lulJOUKYGUfZQojARfdWlklIwEdXVpZJSMBFVVSUSUk5QpgZR9lIwDaW50lIoRp/jihy6R+KuVSQaEFOufmgBzYowLZXhwaXJ5X2RhdGWUTowJc2lnbmF0dXJllE51Yi4="
        )
    )
