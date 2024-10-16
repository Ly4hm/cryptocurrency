import hashlib
import struct
import ecdsa
from ecdsa import VerifyingKey, BadSignatureError
from ecdsa.ellipticcurve import Point
from ecdsa.keys import VerifyingKey
from ecdsa.util import sigdecode_der
from hashlib import sha256

class transaction:

    def __init__(self,hex_string_tx:str):
        #将16进制字符串转变为字节流
        self.hex_bytes_tx=bytes.fromhex(hex_string_tx)
        self.tx=self.parse_transaction(self.hex_bytes_tx)


    #该方法用来处理变长整数
    def parse_varint(self,data, offset):
        value = data[offset]
        offset += 1

            # 确保将字符串或字节正确转换为整数
        if isinstance(value, bytes):
            value = int.from_bytes(value, byteorder='big')
        elif isinstance(value, str):
            value = int(value, 16)
        elif not isinstance(value, int):
            raise TypeError(f"Unexpected type: {type(value)}")

        if value < 0xfd:
            return value, offset#一个字节
        elif value == 0xfd:
            return struct.unpack_from('<H', data, offset)[0], offset + 2  #2字节小端序
        elif value == 0xfe:
            return struct.unpack_from('<I', data, offset)[0], offset + 4  #4字节小端序
        else:
            return struct.unpack_from('<Q', data, offset)[0], offset + 8  #8字节小端序


    #解析交易字节流
    def parse_transaction(self,raw_tx):
        #记录解析二进制字节流的偏移,现在是从头开始解析
        offset = 0
        #返回tx字典
        tx = {}
        
        #解析version
        tx['version'], = struct.unpack_from('<I', raw_tx, offset)#从第1个字节开始解析一个小端序无符号整数（四字节）
        offset += 4
        
        #input Count
        tx['vin_count'], offset = self.parse_varint(raw_tx, offset)
        tx['vin'] = []
        
        #inputs
        for _ in range(tx['vin_count']):
            vin = {}
            
            #之前交易的哈希值（32字节）
            vin['tx_id'] = raw_tx[offset:offset+32][::-1].hex()  # 反转为小端序
            print(vin['tx_id'])
            offset += 32
            
            #上一笔交易的输出索引（四字节）
            vin['vout'], = struct.unpack_from('<I', raw_tx, offset)
            offset += 4
            
            #解锁脚本长度
            vin['script_length'], offset = self.parse_varint(raw_tx, offset)
            
            #解锁脚本，值得注意的是我没有用小端序将整个解锁脚本打包，因为之后这个数据还要进行解析
            vin['script_sig'] = raw_tx[offset:offset + vin['script_length']].hex()#将字节流进行切片
            offset += vin['script_length']
            
            #序列号
            vin['sequence'], = struct.unpack_from('<I', raw_tx, offset)
            offset += 4
            
            tx['vin'].append(vin)
        
        #output count
        tx['vout_count'], offset = self.parse_varint(raw_tx, offset)
        tx['vout'] = []
        
        #output
        for _ in range(tx['vout_count']):
            vout = {}
            
            #交易金额
            vout['value'], = struct.unpack_from('<Q', raw_tx, offset)
            offset += 8
            
            #锁定脚本长度
            vout['script_length'], offset = self.parse_varint(raw_tx, offset)
            
            #锁定脚本
            vout['script_pubkey'] = raw_tx[offset:offset + vout['script_length']].hex()
            offset += vout['script_length']
            
            tx['vout'].append(vout)
        
        #锁定时间
        tx['locktime'], = struct.unpack_from('<I', raw_tx, offset)
        offset += 4
        
        return tx
    

    #解析解锁脚本，返回两个值：sig和pubK
    def parse_script_sig(self):
        offset=0
        #字符串
        raw_sig=bytes.fromhex(self.tx['vin'][0]['script_sig'])

        #解析签名

        sig_length,offset=self.parse_varint(raw_sig, offset)
        sig=raw_sig[offset:offset + sig_length]
        offset+=sig_length

        #解析公钥
        pubK_length,offset=self.parse_varint(raw_sig, offset)
        pubK=raw_sig[offset:offset + pubK_length]


        return sig,pubK
    
    #解析锁定脚本,返回pubK_Hash
    def parse_script_pubkey(self):
        offset=0
        raw_script_pubkey=bytes.fromhex(self.tx['vout'][1]['script_pubkey'])

        _,offset=self.parse_varint(raw_script_pubkey,offset)
        _,offset=self.parse_varint(raw_script_pubkey,offset)
        hash_length,offset=self.parse_varint(raw_script_pubkey,offset)

        pubK_Hash=raw_script_pubkey[offset:offset + hash_length]
        return pubK_Hash
    


class Stack:
    #栈中所存都是bytes的字节数据
    def __init__(self):
        self.index = 0
        self.list = []
    #出栈操作
    def pop(self) -> bytes:
        #栈是否为空
        if self.list:
            self.index-=1
            return self.list.pop()
        else:
            raise IndexError("pop from an empty stack")
        
    #入栈操作
    def push(self,rsp:bytes):
        self.list.append(rsp)
        self.index+=1
    #验证两个哈希值是否相等
    def equl_verify(self) -> bool:
        left=self.pop()
        right=self.pop()
        if left == right:
            return True
        else:
            return False
    #验证签名
    def check_sig(self,tx:transaction) -> bool:
        try:
            #x,y的字节流
            pubK=self.pop()
            #DER格式的字节流
            sig=self.pop()
            #SECP256k1 曲线及其生成元
            curve=ecdsa.SECP256k1.curve

            x_bytes= pubK[1:33]
            y_bytes= pubK[33:65]

            #消息的哈希
            message_hash=tx.tx['vin'][0]['tx_id']

            #大端序解析x,y字节流为整数
            x = int.from_bytes(x_bytes, 'big')
            y = int.from_bytes(y_bytes, 'big')
            
            #检查点是否在曲线上
            if not curve.contains_point(x,y):
                print("Error: Point provided by public key is not on the curve.")
                return False
            
            public_point=Point(curve,x,y)
            vk=VerifyingKey.from_public_point(public_point, curve=ecdsa.SECP256k1)

            valid = vk.verify(sig, bytes.fromhex(message_hash), sigdecode=sigdecode_der, hashfunc=sha256)
            return valid
        except IndexError:
            # 当栈为空时 pop 可能抛出 IndexError
            print("Error: Not enough elements in the stack to pop.")
            return False
        except ValueError as e:
            # 可能在处理字节转换时出现 ValueError
            print(f"Error: {e}")
            return False
        except BadSignatureError:
            # 签名无效
            print("Error: The signature is invalid.")
            return False
        except Exception as e:
            # 捕获其他任意异常
            print(f"Unexpected error: {e}")
            return False


    #哈希函数
    def hash160(self):
        data=self.pop()
        sha256_hash = hashlib.sha256(data).digest()
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)
        ripemd160_hash=ripemd160.digest()
        self.push(ripemd160_hash)

    #复制栈顶内容
    def dup(self):
        rsp=self.pop()
        self.push(rsp)
        self.push(rsp)
        