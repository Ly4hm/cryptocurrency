# Server 接口文档
## sign_coin

```python
def sign_coin(blinded_coin_without_signature_base64: str, userid: str) -> str:
```
**描述**: 对盲化后的货币数据进行签名，并返回签名后的 base64 编码字符串。
**参数**:
- blinded_coin_without_signature_base64 (str): 经过 base64 编码、序列化和盲化后的 Coin 对象数据。
- userid (str): 请求签名的用户ID。

**返回**:
str: 签名后的 base64 编码字符串。

**行为**:
解码 blinded_coin_without_signature_base64 以获取盲化的货币数据。
使用签名机器对盲化的数据进行签名。
扣除用户的一次签名机会。
返回签名后的数据。

## deliver_pub_key
```python
def deliver_pub_key() -> str:
```
**描述**: 分发银行的公钥。
**返回**:
str: 公钥的 base64 编码字符串。
**行为**:
将公钥转化为 PEM 格式字节串。
对 PEM 格式的公钥进行序列化和 base64 编码。
返回编码后的公钥。

## exchange
```python
def exchange(coin: str, userid: str) -> bool:
```
**描述**: 将货币兑换为签名机会，货币的格式为 base64(coin_pickle):base64(signature)，返回兑换是否成功。
**参数**:
- coin (str): 货币数据，格式为 base64(coin_pickle):base64(signature)。
- userid (str): 发起兑换请求的用户ID。

**返回**:
bool: 兑换成功返回 True，否则返回 False。
**行为**:
解码并验证货币和签名数据。
验证成功后，记录货币的使用并增加用户的签名机会。
返回兑换结果。

## register
```python
def register(passwd: str) -> None:
```
**描述**: 注册新用户，生成5位随机的用户ID，并将密码存储为哈希值。
**参数**:
passwd (str): 用户输入的密码。
**行为**:
生成5位随机用户ID。
对输入的密码进行SHA-256哈希处理。
将用户数据插入数据库。
初始为用户设置10次签名机会。