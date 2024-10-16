import hashlib
import struct

class transaction:

    def _init_(self,hex_string_tx:str):
        #将16进制字符串转变为字节流
        self.hex_bytes_tx=bytes.fromhex(hex_string_tx)
        self.tx=self.parse_transaction(self.hex_bytes_tx)


    #该方法用来处理变长整数
    def parse_varint(data, offset):
        value = data[offset]
        offset += 1
        
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
    

    #解析解锁脚本
    def parse_script_sig(self):
        #TODO
        pass
    #解析锁定脚本
    def parse_script_pubkey(self):
        #TODO
        pass

class Stack:
    #栈中所存都是bytes的字节数据
    def _init_(self):
        self.index = 0
        self.list = []
    #出栈操作
    def pop(self,rsp:bytes) -> bytes:
        #栈是否为空
        if self.list:
            self.index-=1
            return self.list.pop()
        else:
            #TODO 错误处理
            pass
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
    #验证签名
    def check_sig():
        # TODO
        pass

    #哈希函数
    def hash160(self):
        data=self.pop()
        sha256_hash = hashlib.sha256(data).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        self.push(ripemd160_hash)

    #复制栈顶内容
    def dup(self):
        rsp=self.list[self.index]
        self.push(rsp)
        