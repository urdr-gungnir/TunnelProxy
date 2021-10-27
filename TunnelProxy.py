import socket
import sys
import datetime
import argparse
import threading
import time

import requests
from threading import Thread
import base64
import re


class MyThread(Thread):
    def __init__(self):
        super(MyThread, self).__init__()
        self.exitcode = 0


    def run(self, coon, addr):
        global ip_ports
        try:
            flag = 0
            pxip, pxport = GetOneEffectIpPort()
            AConnectFromClient(conn, addr, pxip, pxport)
        except ConnectionRefusedError:
            print("ConnectionError")
            flag += 1
            if flag > 3:
                ip_ports.remove(pxip+':'+pxport)
                flag = 0

        except TimeoutError:
            print("连接超时")
            flag += 1
            if flag > 3:
                ip_ports.remove(pxip+':'+pxport)
                flag = 0

        except KeyboardInterrupt:
            self.exitcode = 1
            sys.exit()
        except Exception as e:
            print('other Exception')
            print("异常信息:", end="")
            self.exitcode = 1
            print(e)

def CheckEffectiveness(proxy):
    proxies = {'http': "socks5://{}/".format(proxy), "https": "socks5://{}/".format(proxy)}
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    }

    res = True
    try:
        request = requests.get(url='https://www.baidu.com', headers=header, proxies=proxies, timeout=10)
        if request.status_code == 200:
            res = False
    except ValueError:
        print("缺少pysocks库，请pip安装")
        sys.exit()
    except:
        res = True
    return res

def ReIp(res):
    global ip_ports
    ip_ports += re.findall(r"icp:a,id:\"(.*?)\"", res)



def ChooseUrl(i):
    base_query = 'protocol=="socks5" && "Version:5 Method:No Authentication(0x00)"'


    extra_query = ' && country="CN" && after="{}" && before="{}"'.format(after, before)
    query = base_query + extra_query
    print("[*]query:{}".format(query))
    url = 'https://fofa.so/result?qbase64='+str(base64.b64encode(query.encode(encoding='utf-8')), 'utf-8')+'&page={}&page_size=10'.format(i)
    return url

def GetPxByFofa():
    global ip_ports
    try:
        for i in range(1,6):
            fofa_url = ChooseUrl(i)
            res = requests.get(url=fofa_url, headers=header, timeout=10)
            print("[*]第{}页请求状态码:{}".format(i, res.status_code))
            if(res.status_code != 200):
                print("[*]请检查网络哟")
                sys.exit()
            ReIp(res.text)
            time.sleep(5)

        for i in range(len(ip_ports) - 1, -1, -1):
            ip_port = ip_ports[i]
            if re.search('[a-zA-Z]]', ip_port):
                ip_ports.remove(ip_port)
                continue
            if CheckEffectiveness(ip_port):
                ip_ports.remove(ip_port)
                print('[*]{}不行'.format(ip_port))
                continue
            print('[*]{}行'.format(ip_port))
        # with open("proxies.txt", 'w') as f:
        #     for ip_port in ip_ports:
        #         f.write(ip_port+'\n')

        print("[*]fofa未登录，一共找到{}个有效代理".format(len(ip_ports)))
        if len(ip_ports) == 0:

            print("请重启系统。")
            sys.exit()
    except Exception as e:
        print("[*]网络有问题，请检查")
        print("[*]异常信息为:", end='')
        print(e)
        sys.exit()

def GetOneEffectIpPort():
    global ip_ports
    # with open("proxies.txt", 'r') as f:
    #     ip_port = f.readline().strip("\n")
    #     ip = str(ip_port.split(":")[0])
    #     port = int(ip_port.split(":")[1])
    #     return ip, port
    if ip_ports:
        ip_port = ip_ports[0]
        ip = str(ip_port.split(":")[0])
        port = int(ip_port.split(":")[1])
        return ip, port
    else:
        print("代理池没代理了")
        sys.exit()

def ProxyToClient(conn, toPx):
    j = 0
    while True:
        try:
            data = toPx.recv(1024)
            if not data:
                if j > nodatatime:
                    conn.close()
                    toPx.close()
                    return
                j += 1
        except:
            if j > nodatatime:
                conn.close()
                toPx.close()
                return
            j += 1
        try:
            conn.sendall(data)
        except:
            pass

def ClientToProxy(conn, toPx):
    j = 0
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                if j > nodatatime:
                    conn.close()
                    toPx.close()
                    return
                j += 1
        except Exception as e:
            if j > nodatatime:
                conn.close()
                toPx.close()
                return
            j += 1
            print("[*]错误信息：",end='')
            print(e)
            print("[*] close")
        try:
            toPx.sendall(data)
        except:
            print("[*] send data to proxy error")


def AConnectFromClient(conn, addr, pxip, pxport):
    print("[*] {} connect".format(addr))

    # pxip = '153.3.127.33'
    # pxport = 10

    toPX = socket.socket()
    toPX.connect((pxip, pxport))
    threading.Thread(target=ClientToProxy, args=(conn, toPX)).start()
    threading.Thread(target=ProxyToClient, args=(conn, toPX)).start()



if __name__ == "__main__":

    nodatatime = 3

    parser = argparse.ArgumentParser(description='''
       (￢︿̫̿￢☆)，哼，可恶! 竟然发现我了.
        (ˉ▽￣～)   既然发现我了，那就给你吧！
       ''')
    parser.add_argument("-a", "--after", help='时间范围搜索socks5代理，某时间之后，格式 2021-10-25 10:00:00，如果有具体时间，需要加引号', dest="after")
    parser.add_argument("-b", "--before", help='时间范围搜索socks5代理，某时间之前，格式 2021-10-25 10:00:00，如果有具体时间，需要加引号', dest="before")
    parser.add_argument("-c", "--cookie", help='先去fofa登录，把cookie复制下来，不然只能请求一页代理，代理池会很小', dest="cookie")
    args = parser.parse_args()
    options = vars(args)


    after = datetime.date.today() - datetime.timedelta(days=1)
    before = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not options['cookie']:
        sys.exit("cookie是必要的")
    if options['after']:
        after = options['after']

    if options['before']:
        before = options['before']

    cookie = options['cookie']

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        'Cookie': cookie
    }

    print("[*]寻找可用代理")
    ip_ports = []
    GetPxByFofa()



    sever = socket.socket()


    host = "127.0.0.1"
    port = 9870
    sever.bind((host, port))

    sever.listen(20)

    print("[*] Listening Port 9870 ...")

    while True:
        try:
            conn, addr = sever.accept()
            thread = MyThread()
            thread.run(conn, addr)
            if thread.exitcode != 0:
                print("bye~")
                sys.exit()
        except:
            print("[*] connect from client error")