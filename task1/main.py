from utils import SignatureMachine
from pprint import pprint
import base64

app = Flask(__name__)

if __name__ == "__main__":
    signature_machine = SignatureMachine()
    message = "hello world"
    message_signed = signature_machine.sign(message)

    print(message_signed)
    
    print(signature_machine.verify(message_signed))
