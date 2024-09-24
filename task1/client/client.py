import argparse
from client_core import Client


parser = argparse.ArgumentParser(description='a democoin',prog='Command-line client')

subparsers = parser.add_subparsers(dest='command')

Cline = Client

#生成货币
parser_generate = subparsers.add_parser('gner')
parser_generate.add_argument('amount', type = str, help = '数量')

# 消息盲化
parser_blind = subparsers.add_parser('sig', help='签名')
parser_blind.add_argument('message', type = str, help = '需要签名的coin')

#验证签名
parser_verify = subparsers.add_parser('verf', help = '验证签名')
parser_verify.add_argument('message',  type = str, help = '需要验证的coin')
parser_verify.add_argument('signature', type = str, help = '签名')

args=parser.parse_args()
if args.command == 'sig':
    bite_coin = Cline.view_coin(args.message)[1]
    result = Cline.get_signature(bite_coin)
