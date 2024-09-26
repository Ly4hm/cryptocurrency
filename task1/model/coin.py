from datetime import datetime

import base64
import uuid


class Coin:
    "货币"

    def __init__(self, expiry_date: datetime = None) -> None:
        self._uid = uuid.uuid4()
        self.expiry_date = expiry_date
        self.signature: bytes = None

    def __str__(self) -> str:
        return "UUID:{}\n过期时间:{}".format(
            self.uid, self.expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        )

    @property
    def uid(self):
        "uid读取器"
        return str(self._uid)
