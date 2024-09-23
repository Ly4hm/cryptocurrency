from utils import SignatureMachine
from Crypto.PublicKey import RSA
import hashlib

if __name__ == "__main__":
    key = RSA.generate(2048)
    n = key.n
    e = key.e
    d = key.d
    message = b"123456"
    hash_value = hashlib.md5(message).hexdigest()
    h_int = int(hash_value, 16)

    blinded_message,r = SignatureMachine.blind_message(message,n,e)
    signed_blinded_message = SignatureMachine.sign(blinded_message,d,n)
    signed_message = SignatureMachine.sign(h_int,d,n)
    unblinded_signature = SignatureMachine.unblind_message(signed_blinded_message, r, n)

    print("Unblinded Signature:", unblinded_signature)
    print("original Signature:", signed_message)
    