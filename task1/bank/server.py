import os
import pickle
import sqlite3
import sys

from datetime import datetime
from typing import Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.coin import Coin
from model.user import User


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
        pass

    def sign_coin(coin_without_signature: bytes):
        "将 coin 数据签名，coin 数据为 pickle 序列化后的 Currency 数据"
        pass


if __name__ == "__main__":
    c = Coin()
    print(c.uid)
