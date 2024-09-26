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
        try:
            expiry_time = self.expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        except:
            expiry_time = "Never"

        return "UUID:{}\n过期时间:{}".format(self.uid, expiry_time)

    @property
    def uid(self):
        "uid读取器"
        return str(self._uid)
