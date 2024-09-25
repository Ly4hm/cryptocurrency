# Client 类接口文档
## 概述
Client 类用于实现用户相关的操作，包括消息盲化、签名验证、货币数据生成和查看。

## 方法

## 构造函数

### `__init__`
```python
__init__(pub_key_base64: str, userid: str, server_url: str) -> None


### make_coin
```python
make_coin(expiry_date: datetime = None) -> str
```
  
**描述**: 生成货币数据，返回包含签名的货币字符串。

**参数**:

- expiry_date: 可选，货币的过期日期。如果不提供，则默认为 None。
返回: 生成的货币数据字符串，格式为 coin_data:signature。


### get_signature
```python
get_signature(blinded_coin: bytes) -> bytes
```

**描述**: 获取盲化货币的签名。此方法需要实现与服务器的通信。

**参数**:

- blinded_coin: 盲化后的货币字节流。

**返回**: 返回签名的 Base64 解码后的字节流。

### view_coin
```python
view_coin(coin_b: str) -> tuple
```

**描述**: 解析 Base64 编码后的货币字节流，提取货币 UID 和过期日期。

**参数**:

coin_b: Base64 编码的货币字符串。

**返回**: 一个元组，包含货币的 UID 和过期日期。


### verify_coin
```python
verify_coin(coin: str) -> bool
```

**描述**: 验证给定货币的有效性，包括格式和过期日期的校验。

**参数**:

coin: 由 make_coin 方法生成的货币字符串。
**返回**: 布尔值，表示货币是否有效。