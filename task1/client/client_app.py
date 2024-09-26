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
from runner import Runner


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
    r = method(args)
    if Result.check(r):
        print(r.message)
    else:
        print("[-]", r.message)
