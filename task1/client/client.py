import argparse
import requests
import pickle
import base64
import os
import json
from client_core import Client
from datetime import datetime
#需要转换的类型,base64编码

def register_user(password):
    url = "http://localhost:8008/register"
    headers = {"Content-Type": "application/json"}
    data = {"password": password}
    try:
        response = requests.post(url, headers = headers, json = data)

        if response.status_code == 200:
           print(response.json().get('message','注册成功'))
        elif response.status_code == 400:
            print("错误:", response.json().get('error', '缺少密码'))
        elif response.status_code == 500:
            print("错误:", response.json().get('error', '出错了'))
        else:
            #其他状态码
            print("未知错误，状态代码:", response.status_code)

    except requests.exceptions.RequestException as e:
        print("请求失败:", e)

def recevive_pubkey():
    url = "http://localhost:8008/deliver_pubkey"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            public_key = data.get('public_key')
            if public_key:
                return public_key
            else:
                print("Fail to init Clinet beacuse failde to get public key from response\n")
        elif response.status_code == 500:
            print("错误:", response.json().get('error', '出错了'))
        else:
            print("未知错误，状态代码:", response.status_code)

    except requests.exceptions.RequestException as e:
        print("请求失败:",e)

 
def exchange_coin(coin, userid) -> int:
    url = "http://localhost:8008/exchange"
    headers = {"Content-Type": "application/json"}
    data = {"coin": coin, "userid": userid}
    try:
        response = requests.post(url, headers = headers, json = data)

        if response.status_code == 200:
            return 200
        elif response.status_code == 400:
            return 400
        elif response.status_code == 500:
            return 500
        else:
            return response.status_code
        
    except requests.exceptions.RequestException as e:
        print("请求失败:", e)


#查找用户名相关的userid
def find_user_userid(user:str, file_path) -> str:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                user_data = json.load(f)
            except json.JSONDecodeError:
                user_data = {}
    else:
        user_data = {}

    return user_data.get(user, None)


def store_user_userid(user, userid,file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                user_data = json.load(f)
            except json.JSONDecodeError:
                user_data = {}
    else:
        user_data = {}
    
    user_data[user] = userid

    with open(file_path, 'w') as f:
        json.dump(user_data, f, indent=4)



def store_coin(coin: str, file_path: str):
    try:
        with open(file_path, 'a') as f:
            f.write(coin + '\n')
    except Exception as e:
        print(f"An error occurred: {e}\n")
        
def read_and_remove_coins(num_lines: int, file_path: str):
    try:
        with open(file_path,'r') as f:
            lines = f.readlines()
        
        if lines:
            num_lines_to_read = min(len(lines), num_lines)

            lines_to_return = [line.strip() for line in lines[:num_lines_to_read]]

            remaining_lines = lines[num_lines_to_read:]

            with open(file_path, 'w') as f:
                f.writelines(remaining_lines)
            
            return lines_to_return
        else:
            return []  # 文件为空时返回空列表
    except Exception as e:
        print(f"An error occurred: {e}\n")


def read_coins(file_path: str):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if lines:
            lines_to_return = [line.strip() for line in lines]
            return lines_to_return
        else:
            return []
    except Exception as e:
        print(f"An error occurred: {e}\n")

def decode_getcoin(coin):
    coin_without_signature = coin.split(':')[0]
    coin_byte = coin_without_signature.encode("utf-8")
    coin_pickle = base64.b64decode(coin_byte)
    coin_unpickle = pickle.loads(coin_pickle)
    return coin_unpickle



def main():
    parser = argparse.ArgumentParser(description='a democoin',prog='Command-line client')

    subparsers = parser.add_subparsers(dest='command')

    pub_key_base64 = recevive_pubkey()
    Cline = Client(pub_key_base64=pub_key_base64)

    #生成货币
    parser_generate = subparsers.add_parser('gner', help='生成货币')
    parser_generate.add_argument('-u', '--user', required=True, type = str, help = '用户名')
    parser_generate.add_argument('-a', '--amount', required=True, type = int, help = '数量')
    parser_generate.add_argument('-e', '--expiry_date', type = str, default = None, help = '失效时间例如:2023-09-25 12:30:45')
    parser_generate.add_argument('-r', '--route', required=True, type = str, help = '文件路径')

    #查看货币信息
    parser_view = subparsers.add_parser('view', help='查看货币信息')
    parser_view.add_argument('-r', '--route', required=True, type = str, help = '文件路径')

    #验证签名
    parser_verify = subparsers.add_parser('verf', help = '验证签名')
    parser_verify.add_argument('-m', '--message', required=True,  type = str, help = '需要验证的coin_uid和签名')

    #用户注册逻辑
    parser_register = subparsers.add_parser('reg', help = '用户注册')
    parser_register.add_argument('-u', '--user', required=True, type = str, help = '用户名')
    parser_register.add_argument('-p', '--password', required=True, help = '用户密码')

    #交换货币为签名机会
    parser_exchange = subparsers.add_parser('excg', help = '交换货币为签名机会')
    parser_exchange.add_argument('-u', '--user', required=True, type = str, help = '用户名')
    parser_exchange.add_argument('-a', '--amount', required=True, type = int, help = '数量')
    parser_exchange.add_argument('-r', '--route', required=True, type = str, help = '文件路径')

            

    args=parser.parse_args()
    #接受一个字符串输入，是一个带签名的coin
    if args.command == 'verf':
        coin = args.message 
        coin_unpickle = decode_getcoin(coin)
        coin_uid = coin_unpickle.uid
        status = Cline.verify_coin(coin)
        if status == True:
            print("verify seccssed: %s\n" %coin_uid)
        if status == False:
            print("verify failed: %s\n" %coin_uid)
    
    #生成coin
    elif args.command == 'genr':
        user = args.user
        userid = find_user_userid(user)
        Cline.userid = userid
        amount = args.amount
        time_str = args.expiry_date
        file_path = args.route
        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        #添加申请
        while amount > 0:
            coin = Cline.make_coin(time_obj)
            amount -= 1
            store_coin(coin=coin,file_path=file_path)
        print("生成货币完成\n")

    #查看货币
    elif args.command == 'view':
        file_path = args.route
        coins = read_coins(file_path)
        for coin in coins:
            coin_unpickle = decode_getcoin(coin)
            sig = coin.split(':')[1]
            coin_expiry_date = coin_unpickle.expiry_date
            coin_uid = coin_unpickle.uid
            print("ID:%s Expiry_date:%s sig:%s", coin_uid, coin_expiry_date, sig)
        



    
    #用户注册
    elif args.command == 'reg':
        user = args.user
        password = args.password
        try:
            userid = register_user(password=password)
            store_user_userid(user,userid)
        except Exception as e:
            print(f"An error occurred: {e}\n")

    #交换签名
    elif args.command == 'excg':
        user = args.user
        Cline.userid = find_user_userid(user)
        amount = args.amount
        file_path = args.route
        try:
            coins = read_and_remove_coins(num_lines=amount,file_path=file_path)
            for coin in coins:
                coin_uid = decode_getcoin(coin).uid
                status = exchange_coin(coin, userid)
                if status ==200:
                    print("交换成功", coin_uid)
                else:
                    print("交换失败", coin_uid)
                    store_coin(coin, file_path)
        except Exception as e:
            print(f"An error occurred: {e}\n")
            

if __name__ == "__main__":
    main()