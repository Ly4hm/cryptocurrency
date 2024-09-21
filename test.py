import os
import hashlib
import math
import cryptography
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils


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

        # 获取盲因子
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
        message_int = int.from_bytes(message, "big")
        blinded_message = (
            pow(self.r, self.public_key.public_numbers().e) * message_int
        ) % self.public_key.public_numbers().n
        return self.convert_to_bytes(blinded_message)

    def unblind_signature(self, blinded_signature: bytes) -> bytes:
        "签名去盲化"
        n = self.public_key.public_numbers().n
        blinded_signature_int = int.from_bytes(blinded_signature, "big")        
        # 计算r的模逆元
        r_inv = pow(self.r, -1, n)
        # 计算去盲化后的签名
        signature = (blinded_signature_int * r_inv) % n
        return self.convert_to_bytes(signature)

    def sign_message_without_blind(self, message: bytes) -> bytes:
        # 使用私钥对消息进行签名
        signature = self.private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
        return signature

    def sign_message(self, message: bytes) -> bytes:
        # 消息盲化
        blinded_message = self.blind_message(message)
        
        # 使用私钥对消息进行签名
        blinded_signature = self.private_key.sign(blinded_message, padding.PKCS1v15(), hashes.SHA256())
        signature = self.unblind_signature(blinded_signature)
        return signature

    def verify_signature(self, message: bytes, signature: bytes) -> bool:
        # 使用公钥验证签名
        try:
            self.public_key.verify(
                signature, message, padding.PKCS1v15(), hashes.SHA256()
            )
            return True
        except cryptography.exceptions.InvalidSignature:
            return False

    def convert_to_bytes(self, value: int) -> bytes:
        "将内容转化为bytes"
        return value.to_bytes((value.bit_length() + 7) // 8, byteorder="big")


def test_signature_machine():
    # 实例化 SignatureMachine
    signature_machine = SignatureMachine()

    # 原始消息
    message = b"Test message for RSA signature"

    # 生成普通签名
    signature = signature_machine.sign_message_without_blind(message)
    print("Generated Signature hash:", hashlib.md5(signature).digest().hex())

    # 生成盲签名
    signature_b = signature_machine.sign_message(message)
    print("Generated Blinded Signature hash:", hashlib.md5(signature_b).digest().hex())

    # 验证签名
    is_valid = signature_machine.verify_signature(message, signature_b)
    print("Is the signature valid?", is_valid)
    # assert(is_valid == True)
    
    print(len(signature), len(signature_b))

    # 尝试验证一个伪造的签名（应当返回 False）
    forged_signature = signature[:-1] + bytes(
        [signature[-1] ^ 0x01]
    )  # 修改签名的最后一位
    is_valid_forged = signature_machine.verify_signature(message, forged_signature)
    print("Is the forged signature valid?", is_valid_forged)
    # assert(is_valid_forged == False)


# 运行测试
test_signature_machine()
