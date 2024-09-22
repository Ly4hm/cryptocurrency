from utils import SignatureMachine
from pprint import pprint
import base64


if __name__ == "__main__":
    signature_machine = SignatureMachine()
    message = "hello world"
    signature_machine.rsa_key()
    