import hashlib
import math
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, utils


class BlindingDevice:
    """RSA 盲签名消息盲化器"""

    def __init__(self, public_key) -> None:
        # 获取盲因子
        self.public_key = public_key
        self.r = self._generate_blind_factor()

    def _generate_blind_factor(self):
        "生成盲因子r"
        n = self.public_key.public_numbers().n
        while True:
            r = int.from_bytes(os.urandom(32), byteorder="big") % n
            if math.gcd(r, n) == 1:
                return r

    def blind_message(self, message: bytes) -> bytes:
        "盲化消息"
        digest = hashlib.sha256(message).digest()
        message_int = int.from_bytes(digest, "big")
        n = self.public_key.public_numbers().n
        e = self.public_key.public_numbers().e

        r_e = pow(self.r, e, n)
        blinded_message_int = (message_int * r_e) % n
        return self.convert_to_bytes(blinded_message_int)

    def unblind_signature(self, blinded_signature: bytes) -> bytes:
        "签名去盲化"
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


class SignatureMachine:
    """
    基于 RSA 盲签名的签名器

    Attributes:
        public_key - rsa 公钥
        private_key - rsa 私钥

    Func:
        签名调用：
            sign(message: str) -> signature: str
            输出格式：<message>:<signature>
        验证调用：
            verify(message_and_signature: str) -> bool
            true 验证通过，反之失败
            message_and_signature 参数格式：<message>:<signature>
    """

    def __init__(self):
        # 生成一个新的 RSA 私钥
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        # 获取与之对应的公钥
        self.public_key = self.private_key.public_key()

    def sign_message(self, blinded_message: bytes) -> bytes:
        # 获取私钥参数
        private_numbers = self.private_key.private_numbers()
        d = private_numbers.d
        n = private_numbers.public_numbers.n
        # 将盲化消息转换为整数
        blinded_m_int = int.from_bytes(blinded_message, byteorder="big")
        # 计算盲签名 s' = (blinded_m_int)^d mod n
        s_prime_int = pow(blinded_m_int, d, n)
        # 将盲签名转换为字节
        blinded_signature = s_prime_int.to_bytes(
            (n.bit_length() + 7) // 8, byteorder="big"
        )
        return blinded_signature

    def verify_signature(self, message: bytes, signature: bytes) -> bool:
        # 使用公钥验证签名
        public_numbers = self.public_key.public_numbers()
        e = public_numbers.e
        n = public_numbers.n

        s_int = int.from_bytes(signature, byteorder="big")

        # 计算 m' = (s_int)^e mod n
        m_prime_int = pow(s_int, e, n)

        message_hash = hashlib.sha256(message).digest()
        m_int = int.from_bytes(message_hash, byteorder="big")

        return m_prime_int == m_int

    def get_pub_key(self):
        "返回公钥"
        return self.public_key