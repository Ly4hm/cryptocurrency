import base64
import hashlib
import os
import pickle
import random
import sqlite3
import string
import sys

from datetime import datetime, time
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

        # 创建 user 表
        self.cursor.execute(
            """
CREATE TABLE user (
    userid TEXT PRIMARY KEY CHECK (LENGTH(userid) = 5),
    password TEXT NOT NULL,
    count INTEGER NOT NULL
)
"""
        )

        # 创建 used_coin 表
        self.cursor.execute(
            """
CREATE TABLE used_coin (
    coin_uuid TEXT NOT NULL,
    time INTEGER NOT NULL,
    PRIMARY KEY (coin_uuid)
)
"""
        )
        self.conn.commit()

    def __reduce__(self) -> str | tuple[Any, ...]:
        "垃圾处理"
        self.conn.close()
        self.cursor.close()

    def register(self, password: str, init_count=10):
        "注册一个用户，id为 5位 随机字符串， passwd 为 hash 后的32位字符串，初始赠送10次签名机会"
        # 生成 5 位随机 userid
        userid = "".join(random.choices(string.ascii_letters + string.digits, k=5))

        # 输入密码并进行哈希
        passwd = input("请输入密码: ")
        hashed_passwd = hashlib.sha256(passwd.encode()).hexdigest()
        # 插入用户数据
        self.cursor.execute(
            """
        INSERT INTO user (userid, password, count)
        VALUES (?, ?, ?)
        """,
            (userid, hashed_passwd, 10),
        )

        self.conn.commit()

    def deduct_sign_chance(self, userid) -> bool:
        """扣除一次签名机会，返回是否扣除成功"""
        self.cursor.execute(
            """
        UPDATE user
        SET count = count - 1
        WHERE userid = ? AND count > 0
        """,
            (userid,),
        )
        self.conn.commit()

        if self.cursor.rowcount > 0:
            return True
        else:
            return False

    def add_sign_chance(self, userid):
        """增加一次签名机会"""
        self.cursor.execute(
            """
        UPDATE user
        SET count = count - 1
        WHERE userid = ? AND count > 0
        """,
            (userid,),
        )
        self.conn.commit()

    def insert_used_coin(self, coin_uuid: str):
        """记录使用过的coin"""
        # 获取当前时间戳
        current_time = int(time.time())

        # 插入数据到 used_coin 表
        self.cursor.execute(
            """
        INSERT INTO used_coin (coin_uuid, time)
        VALUES (?, ?)
        """,
            (coin_uuid, current_time),
        )

        self.conn.commit()


class Bank:
    """中央银行"""

    def __init__(self) -> None:
        self.signature_machine = SignatureMachine()
        self.data_map = DataMap("doin.db")

    def sign_coin(self, blinded_coin_without_signature_base64: str, userid: str) -> str:
        """
        将 coin 数据签名

        coin_without_signature_base64 数据为 pickle 序列化后经过 base64 编码 Currency 数据,然后经过盲化

        Return: 签名的 base64 编码
        """
        blinded_coin_without_signature: bytes = base64.b64decode(
            blinded_coin_without_signature_base64
        )
        blinded_signature = self.signature_machine.sign_message(
            blinded_coin_without_signature
        )
        
        # 扣除签名次数
        self.data_map.add_sign_chance(userid)

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

    def exchange(self, coin: str, userid: str) -> bool:
        """将coin兑换为签名机会, coin 格式为 base64(coin_pickle):base64(signature)
        返回兑换结果是否成功"""
        coin, signature = coin.split(":")
        coin = base64.b64decode(coin)
        signature = base64.b64decode(signature)
        if self.signature_machine.verify_signature(coin, signature):
            uuid = pickle.loads(coin).uid
            
            # 更新数据库
            self.data_map.insert_used_coin(uuid)
            self.data_map.add_sign_chance(userid)
            return True
        else:
            return False
        
    def register(self,  passwd):
        """注册新用户"""
        self.data_map.register(passwd)


if __name__ == "__main__":
    b = Bank()
    print(
        b.sign_coin(
            "gASVcgAAAAAAAACMCm1vZGVsLmNvaW6UjARDb2lulJOUKYGUfZQojARfdWlklIwEdXVpZJSMBFVVSUSUk5QpgZR9lIwDaW50lIoRp/jihy6R+KuVSQaEFOufmgBzYowLZXhwaXJ5X2RhdGWUTowJc2lnbmF0dXJllE51Yi4="
        )
    )
