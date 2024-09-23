from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util import number
import random
import hashlib

class SignatureMachine:
    #盲化消息
    def blind_message(message,n,e):
        #MD5哈希
        h = hashlib.md5(message).hexdigest()
        h_int = int(h, 16)
        #生成盲因子r,如果r与 n 不是互质的，就会导致后续计算 r 的模逆元时无法得到有效的逆元，从而影响签名的正确性
        r = random.randint(2,n-1)
        while number.GCD(r, n) != 1:
            r = random.randint(2, n - 1)
        r_e = pow(r, e, n)
        blinded_message = (h_int * r_e) % n
        return blinded_message, r


    def unblind_message(blinded_signature, r, n):
        # 计算 r 的模逆元,用乘以逆元的操作代替除r的操作
        r_inv = number.inverse(r, n)
        # 去盲化 (blinded_signature * r^-1) mod n
        unblinded_signature = (blinded_signature * r_inv) % n
        return unblinded_signature

    def sign(blinded_message,d,n):
        return pow(blinded_message, d, n)

