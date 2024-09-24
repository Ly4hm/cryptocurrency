import hashlib
import math
import os


class BlindingDevice:
    """RSA 盲签名消息盲化器"""

    def __init__(self, public_key) -> None:
        # 获取盲因子
        self.public_key = public_key
        self.r = self._generate_blind_factor()
        
        # 用来给刷新盲因子加锁
        self.unverified_flag = False

    def _generate_blind_factor(self):
        "生成盲因子r"
        n = self.public_key.public_numbers().n
        while True:
            r = int.from_bytes(os.urandom(32), byteorder="big") % n
            if math.gcd(r, n) == 1:
                return r

    def blind_message(self, message: bytes) -> bytes:
        "盲化消息"
        self.unverified_flag = True
        
        digest = hashlib.sha256(message).digest()
        message_int = int.from_bytes(digest, "big")
        n = self.public_key.public_numbers().n
        e = self.public_key.public_numbers().e

        r_e = pow(self.r, e, n)
        blinded_message_int = (message_int * r_e) % n
        return self.convert_to_bytes(blinded_message_int)

    def unblind_signature(self, blinded_signature: bytes) -> bytes:
        "签名去盲化"
        self.unverified_flag = False
        
        n = self.public_key.public_numbers().n
        blinded_signature_int = int.from_bytes(blinded_signature, "big")
        # 计算r的模逆元
        r_inv = pow(self.r, -1, n)
        # 计算去盲化后的签名
        signature = (blinded_signature_int * r_inv) % n
        return self.convert_to_bytes(signature)

    def convert_to_bytes(self, value: int) -> bytes:
        "将内容转化为bytes"
        return value.to_bytes((value.bit_length() + 7) // 8, byteorder="big")

    def fresh_r(self) -> bool:
        """
        刷新 盲因子 r
        - Return: 是否刷新成功
        - 刷新不成功主要是因为当前盲因子还未使用过，可能造成无法解盲化"""
        if self.unverified_flag:
            return False
        self.r = self._generate_blind_factor()
        return True