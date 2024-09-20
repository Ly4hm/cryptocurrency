import base64
import hashlib
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


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

    def __init__(self, key_size=2048) -> None:
        self.key_size = key_size
        self.private_key, self.public_key = self._generate_rsa_keypair()
        self.r = None

    def sign(self, message: str) -> str:
        "对给定的消息进行rsa盲签名"
        signature = self._sign_blinded_message(self._blind_message(message))
        return base64.b64encode(message.encode()).decode("utf-8") + ":" + str(signature)

    def verify(self, message_and_signature: str) -> bool:
        "签名验证，true 验证通过，反之失败"
        return self._verify_signature(message_and_signature)

    def _generate_rsa_keypair(self):
        "生成RSA密钥对"
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
        )
        public_key = private_key.public_key()

        return private_key, public_key

    def _blind_message(self, message) -> int:
        "盲化消息"
        message_hash = int.from_bytes(
            hashlib.sha256(message.encode()).digest(), byteorder="big"
        )
        self.r = (
            int.from_bytes(os.urandom(32), byteorder="big")
            % self.public_key.public_numbers().n
        )

        # 公式：(r^e * m) % n
        blinded_message = (
            pow(
                self.r,
                self.public_key.public_numbers().e,
                self.public_key.public_numbers().n,
            )
            * message_hash
        ) % self.public_key.public_numbers().n

        return blinded_message

    def _sign_blinded_message(self, blinded_message) -> int:
        "盲化签名"
        blinded_signature = self.private_key.sign(
            blinded_message.to_bytes(
                (blinded_message.bit_length() + 7) // 8, byteorder="big"
            ),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return int.from_bytes(blinded_signature, byteorder="big")

    def _unblind_signature(self, blinded_signature):
        n = self.public_key.public_numbers().n
        # 计算r的模逆元
        r_inv = pow(self.r, -1, n)
        # 计算去盲化后的签名
        signature = (blinded_signature * r_inv) % n
        return signature

    def _verify_signature(self, message_and_signature) -> bool:
        "验证签名"
        # 解码消息
        message, blinded_signature = message_and_signature.split(":")
        message = base64.b64decode(message).decode("utf-8")
        signature = self._unblind_signature(int(blinded_signature))

        message_hash = int.from_bytes(
            hashlib.sha256(message.encode()).digest(), byteorder="big"
        )
        recovered_hash = pow(
            signature,
            self.public_key.public_numbers().e,
            self.public_key.public_numbers().n,
        )

        print(recovered_hash)
        print(self.sign(message))

        return recovered_hash == self.sign(message)


if __name__ == "__main__":
    signature_machine = SignatureMachine()
    message = "hello world"
    message_signed = signature_machine.sign(message)

    # print(message_signed)

    print(signature_machine.verify(message_signed))
