import argparse
import base64
import hashlib
import json
import os
import sys
import pickle
from datetime import datetime
import time

from client_core import Client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from model.result import Result


class Runner:
    """
    命令行功能实现
    """

    def __init__(
        self, host: str, port: str, userid: str = None, passwd: str = None
    ) -> None:
        self.server_addr = f"http://{host}:{port}/"
        self.userid = userid
        self.passwd = passwd
    
    def set_client_core(self, client: Client):
        """设置 clint_core"""
        self.client = client

    def register(self) -> Result:
        """注册用户"""
        url = self.server_addr + "register"
        headers = {"Content-Type": "application/json"}
        data = {"password": self.passwd}
        try:
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                return Result.ok(response.json().get("message", "注册成功"))
            else:
                return Result.err(
                    response.json().get(
                        "message",
                        "未知错误，状态代码: {}".format(response.status_code),
                    )
                )
        except requests.exceptions.RequestException as e:
            return Result.err(f"请求失败: {e}")

    def view(self, path: str) -> Result:
        """查看指定 coin 文件的货币信息"""
        try:
            with open(path, "r") as coin_file:
                coin_base64, signature_base64 = coin_file.read().strip().split(":")
                signature_hash = (
                    hashlib.sha256(base64.b64decode(signature_base64)).digest().hex()
                )
                coin: str = str(pickle.loads(base64.b64decode(coin_base64)))
                return Result.ok("{}\n签名Hash: {}".format(coin, signature_hash))
        except:
            return Result.err("文件读取错误")

    def generate(self, path: str = "Coin_{}.coin".format(time.time())) -> Result:
        """生成 coin"""
        if not self.verify_user():
            return Result.err("身份验证失败")
        
        coin_string = self.client.make_coin()
        try:
            with open(path, "w") as coin_file:
                coin_file.write(coin_string)
                return Result.ok("coin 生成成功")
        except Exception as e:
            return Result.err(f"coin 写入失败 {e}")

    def exchange(self, coin: str, userid: str) -> int:
        """兑现coin"""
        url = self.server_addr + "exchange"
        headers = {"Content-Type": "application/json"}
        data = {"coin": coin, "userid": userid}
        try:
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                return Result.ok()

        except requests.exceptions.RequestException as e:
            return Result.err(str(e))
        
    def verify_user(self) -> bool:
        """判断用户是否有效"""
        try:
            url = self.server_addr + "verify_user"
            data = {"userid": self.userid, "passwd": hashlib.sha256(self.passwd.encode()).digest().hex()}
            print(data)
            res = requests.post(url, json=data)
            
            if res.status_code == 200:
                return True
            else:
                print(res.text)
                return False
            
        except Exception as e:
            print(f"身份验证请求发起失败: {e}")
            sys.exit(1)

    def get_pubkey(self) -> str:
        """从服务器获取公钥"""
        url = self.server_addr + "deliver_pubkey"
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                public_key = data.get("public_key")
                if public_key:
                    return public_key
        except requests.exceptions.RequestException as e:
            return None

    def _parse_time(self, date_string: str) -> datetime:
        """ "将字符串解析为 datetime 类"""
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

    def _store_coin(coin: str, file_path: str) -> Result:
        """将 base64 编码过的 coin 存储至指定文件"""
        try:
            with open(file_path, "a") as f:
                f.write(coin + "\n")
            return Result.ok()
        except Exception as e:
            return Result.err("coin 存储失败")

    def _parse_coin(self, path: str) -> list:
        "从文件中提取出coin字符串"
        with open(path, "r") as coin_file:
            return coin_file.read().strip().split(":")


# 参数解析
parser = argparse.ArgumentParser(description="Doin trading client", prog="Doin Client")

parser.add_argument(
    "-bh", "--bank-host", required=True, type=str, help="Bank 服务器地址"
)
parser.add_argument(
    "-bp", "--bank-port", required=True, type=str, help="Bank 服务器端口"
)

subparsers = parser.add_subparsers(dest="sub_command_name")
parser_generate = subparsers.add_parser("generate", help="生成coin")
parser_view = subparsers.add_parser("view", help="查看coin信息")
parser_verify = subparsers.add_parser("verify", help="验证签名")
parser_exchange = subparsers.add_parser("exchange", help="交换货币为签名机会")
parser_register = subparsers.add_parser("register", help="用户注册")


# 生成货币
parser_generate.add_argument("-u", "--userid", required=True, type=str, help="用户名")
parser_generate.add_argument("-p", "--password", required=True, help="用户密码")
parser_generate.add_argument(
    "-e",
    "--expiry-date",
    required=False,
    type=str,
    default=None,
    help="失效时间, 样例:2023-09-25 12:30:45",
)
parser_generate.add_argument(
    "-o", "--out-path", required=False, type=str, help="导出文件路径"
)

# 查看货币信息
parser_view.add_argument(
    "-c", "--coin", required=True, type=str, help="需要验证的coin路径"
)

# 验证签名
parser_verify.add_argument(
    "-c", "--coin", required=True, type=str, help="需要验证的coin路径"
)

# 用户注册逻辑
parser_register.add_argument("-p", "--password", required=True, help="用户密码")

# 交换货币为签名机会
parser_exchange.add_argument("-u", "--userid", required=True, type=str, help="用户ID")
parser_exchange.add_argument(
    "-c", "--coin", required=True, type=str, help="coin 文件路径"
)


args = parser.parse_args()

print(args)

# 初始化
passwd = getattr(args, "password", None)
userid = getattr(args, "userid", None)

runner = Runner(args.bank_host, args.bank_port, userid, passwd)

# 获取公钥
public_key = runner.get_pubkey()
if not public_key:
    print("获取公钥失败")
    sys.exit(1)


client = Client(public_key, userid, "http://{}:{}/".format(args.bank_host, args.bank_port))

runner.set_client_core(client)

# 反射调用
method = getattr(runner, str(args.sub_command_name), None)

if callable(method):
    r = method()
    if Result.check(r):
        print(r.message)
    else:
        print("[-]", r.message)
