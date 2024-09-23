import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bank.utils import *
from client.utils import *

class TestRSABlindSignature(unittest.TestCase):
    """RSA 盲签名相关单元测试"""

    def test_sign(self):
        signature_machine = SignatureMachine()
        blind_device = BlindingDevice(signature_machine.get_pub_key())

        message = b"Test message for RSA signature"

        # 盲化
        blinded_message = blind_device.blind_message(message)
        # 对盲化消息签名
        signature_b = signature_machine.sign_message(blinded_message)
        # 签名去盲化
        signature = blind_device.unblind_signature(signature_b)
        # 签名验证
        self.assertTrue(signature_machine.verify_signature(message, signature))

        # 尝试验证一个伪造的签名（应当返回 False）
        forged_signature = signature[:-1] + bytes(
            [signature_b[-1] ^ 0x01]
        )  # 修改签名的最后一位
        self.assertFalse(signature_machine.verify_signature(message, forged_signature))


if __name__ == "__main__":
    unittest.main()
