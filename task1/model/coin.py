from datetime import datetime
import uuid


class Coin:
    "货币"

    def __init__(self, expiry_date: datetime = None) -> None:
        self._uid = uuid.uuid4()
        self.expiry_date = expiry_date

    @property
    def uid(self):
        "uid读取器"
        return str(self._uid)
