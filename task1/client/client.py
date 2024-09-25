import argparse
import pickle
from client_core import Client
#需要转换的类型,base64编码

parser = argparse.ArgumentParser(description='a democoin',prog='Command-line client')

subparsers = parser.add_subparsers(dest='command')

Cline = Client

#生成货币
parser_generate = subparsers.add_parser('gner')
parser_generate.add_argument('amount', type = int, help = '数量')
parser_generate.add_argument('expiry_date', type = str, default = None, help = '失效时间')

#查看货币信息
parser_generate = subparsers.add_parser('view')
parser_generate.add_argument('amount', type = int, help = '数量')

#验证签名
parser_verify = subparsers.add_parser('verf', help = '验证签名')
parser_verify.add_argument('message',  type = str, help = '需要验证的coin')



args=parser.parse_args()
#接受一个字符串输入，是一个带签名的coin
if args.command == 'verf':
    coin = args.message
    coin_uid = pickle.load(coin.split(':')[0])
    status = Cline.verify_coin(coin)
    if status == True:
        print("verify seccssed: %s" %coin_uid)
    if status == False:
        print("verify failed: %s" %coin_uid)
if args.command == 'genr':
    amount = args.amount
    str_time = args.expiry_date
    coin = Cline.make_coin
    

