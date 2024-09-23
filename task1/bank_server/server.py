from typing import Any
import uuid
import sqlite3


class Currency:
    "货币"

    def __init__(self, owner) -> None:
        self.uid = uuid.uuid4()
        self.owner = owner

    @property
    def get_uid(self):
        "uid读取器"
        return str(self.uid)

    @property
    def get_owner(self) -> str:
        "读取所有者"
        return self.owner


class CurrencyPrinter:
    "印钞机"

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

    def grant(owner: str):
        "发放货币"
        currency = Currency(owner)


if __name__ == "__main__":
    c = Currency("ff")
    print(c.uid)
