# Flask 应用接口文档

## 概述

本Flask应用提供了一个基于RSA盲签名的交易系统的API接口，主要用于用户注册、货币签名、货币交换、分发公钥以及验证货币签名的有效性。以下文档详细描述了各个API端点的用途、请求参数、响应格式及示例。

## API 端点

### 1. 注册新用户

#### `POST /register`

**描述**: 注册一个新用户，生成唯一的用户ID，并为其分配初始签名次数。

**请求参数**:

- **Content-Type**: `application/json`
- **Body**:
  - `password` (字符串, 必填): 用户的密码。

**请求示例**:
```bash
curl -X POST http://localhost:8008/register \
     -H "Content-Type: application/json" \
     -d '{"password": "your_password"}'
```

**响应**:

- **成功** (`200 OK`):
  ```json
  {
    "message": "账号注册成功"
  }
  ```

- **失败** (`400 Bad Request` 或 `500 Internal Server Error`):
  ```json
  {
    "error": "缺少密码"
  }
  ```
  或
  ```json
  {
    "error": "出错了: <错误信息>"
  }
  ```

---

### 2. 分发公钥

#### `GET /deliver_pubkey`

**描述**: 分发服务器的RSA公钥，供客户端用于消息盲化。

**请求参数**: 无

**请求示例**:
```bash
curl -X GET http://localhost:8008/deliver_pubkey
```

**响应**:

- **成功** (`200 OK`):
  ```json
  {
    "public_key": "<base64_encoded_public_key>"
  }
  ```

- **失败** (`500 Internal Server Error`):
  ```json
  {
    "error": "出错了，原因为 <错误信息>"
  }
  ```

---

### 3. 签名盲化货币

#### `POST /sign_coin`

**描述**: 接收客户端盲化后的货币数据和用户ID，生成签名并返回签名结果。

**请求参数**:

- **Content-Type**: `application/json`
- **Body**:
  - `blinded_coin_without_signature_base64` (字符串, 必填): Base64编码的盲化后的序列化货币数据。
  - `userid` (字符串, 必填): 用户的唯一标识符。

**请求示例**:
```bash
curl -X POST http://localhost:8008/sign_coin \
     -H "Content-Type: application/json" \
     -d '{
           "blinded_coin_without_signature_base64": "base64_encoded_blinded_coin",
           "userid": "ABCDE"
         }'
```

**响应**:

- **成功** (`200 OK`):
  ```json
  {
    "signature": "<base64_encoded_signature>"
  }
  ```

- **失败** (`400 Bad Request` 或 `500 Internal Server Error`):
  ```json
  {
    "error": "缺少参数"
  }
  ```
  或
  ```json
  {
    "error": "出错了: <错误信息>"
  }
  ```

---

### 4. 交换货币为签名机会

#### `POST /exchange`

**描述**: 将已签名的货币兑换为签名机会。

**请求参数**:

- **Content-Type**: `application/json`
- **Body**:
  - `coin` (字符串, 必填): 货币字符串，格式为 `base64(coin_pickle):base64(signature)`。
  - `userid` (字符串, 必填): 用户的唯一标识符。

**请求示例**:
```bash
curl -X POST http://localhost:8008/exchange \
     -H "Content-Type: application/json" \
     -d '{
           "coin": "base64_encoded_coin:base64_encoded_signature",
           "userid": "ABCDE"
         }'
```

**响应**:

- **成功** (`200 OK`):
  ```json
  {
    "message": "交换成功"
  }
  ```

- **失败** (`400 Bad Request` 或 `500 Internal Server Error`):
  ```json
  {
    "message": "交换失败"
  }
  ```
  或
  ```json
  {
    "error": "出错了: <错误信息>"
  }
  ```

---

### 5. 验证货币签名

#### `POST /verify_signature`

**描述**: 验证货币的签名是否有效。

**请求参数**:

- **Content-Type**: `application/json`
- **Body**:
  - `coin_base64` (字符串, 必填): Base64编码的序列化货币数据。
  - `signature_base64` (字符串, 必填): Base64编码的签名数据。

**请求示例**:
```bash
curl -X POST http://localhost:8008/verify_signature \
     -H "Content-Type: application/json" \
     -d '{
           "coin_base64": "base64_encoded_coin",
           "signature_base64": "base64_encoded_signature"
         }'
```

**响应**:

- **签名有效** (`200 OK`):
  ```json
  {
    "valid": true,
    "message": "签名有效"
  }
  ```

- **签名无效** (`400 Bad Request`):
  ```json
  {
    "valid": false,
    "message": "签名无效"
  }
  ```

- **失败** (`400 Bad Request` 或 `500 Internal Server Error`):
  ```json
  {
    "error": "缺少参数"
  }
  ```
  或
  ```json
  {
    "error": "出错了: <错误信息>"
  }
  ```

---

## 示例请求与响应

### 示例 1: 注册用户

**请求**:
```bash
curl -X POST http://localhost:8008/register \
     -H "Content-Type: application/json" \
     -d '{"password": "secure_password"}'
```

**响应**:
```json
{
  "message": "账号注册成功"
}
```

### 示例 2: 获取公钥

**请求**:
```bash
curl -X GET http://localhost:8008/deliver_pubkey
```

**响应**:
```json
{
  "public_key": "gASVygEAAAAAAABCwwEAAC0tLS0tQkVHSU4gUFVCTElDIEtFWS0tLS0tCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBc0orWXJNaXlrZ1laRkg2ejJ0WmoK..."
}
```

### 示例 3: 签名盲化货币

**请求**:
```bash
curl -X POST http://localhost:8008/sign_coin \
     -H "Content-Type: application/json" \
     -d '{
           "blinded_coin_without_signature_base64": "gASVcgAAAAAAAACMCm1vZGVsLmNvaW6UjARDb2lulJOUKYGUfZQojARfdWlklIwEdXVpZJSMBFVVSUSUk5QpgZR9lIwDaW50lIoRp/jihy6R+KuVSQaEFOufmgBzYowLZXhwaXJ5X2RhdGWUTowJc2lnbmF0dXJllE51Yi4=",
           "userid": "ABCDE"
         }'
```

**响应**:
```json
{
  "signature": "base64_encoded_signature"
}
```

### 示例 4: 交换货币

**请求**:
```bash
curl -X POST http://localhost:8008/exchange \
     -H "Content-Type: application/json" \
     -d '{
           "coin": "base64_encoded_coin:base64_encoded_signature",
           "userid": "ABCDE"
         }'
```

**响应**:
```json
{
  "message": "交换成功"
}
```

### 示例 5: 验证签名

**请求**:
```bash
curl -X POST http://localhost:8008/verify_signature \
     -H "Content-Type: application/json" \
     -d '{
           "coin_base64": "base64_encoded_coin",
           "signature_base64": "base64_encoded_signature"
         }'
```

**响应** (签名有效):
```json
{
  "valid": true,
  "message": "签名有效"
}
```

**响应** (签名无效):
```json
{
  "valid": false,
  "message": "签名无效"
}
```

---

## 注意事项

1. **参数验证**:
   - 所有需要的参数必须在请求体中提供，否则服务器将返回 `400 Bad Request` 错误。
   - 确保参数类型和格式正确，例如Base64编码的字符串。

2. **错误处理**:
   - 服务器在发生异常时，会返回 `500 Internal Server Error`，并在响应中包含错误信息。
   - 客户端应根据错误信息采取相应的处理措施。

3**服务器启动**:
   - 确保在运行 `app.py` 前，所有依赖和数据库配置正确。
   - 启动服务器：
     ```bash
     python app.py
     ```
   - 服务器将运行在 `http://localhost:8008`，可以根据需要修改端口号。