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


    def run(self, conn, addr):
        global ip_ports
        try:
            flag = 0
            pxip, pxport = GetOneEffectIpPort()
            AConnectFromClient(conn, addr, pxip, pxport)
        except ConnectionRefusedError:
            Eprint("ConnectionError")
            flag += 1
            if flag > 3:
                ip_ports.remove(pxip+':'+pxport)
                flag = 0

        except TimeoutError:
            Eprint("连接超时")
            flag += 1
            if flag > 3:
                ip_ports.remove(pxip+':'+pxport)
                flag = 0

        except KeyboardInterrupt:
            self.exitcode = 1
            sys.exit()
        except Exception as e:
            Eprint('other Exception')
            Eprint("异常信息:", end="")
            self.exitcode = 1
            Eprint(e)

def Eprint(text):
    print("\033[31m{}\033[0m".format(text))


def CheckEffectiveness(proxy, web):
    proxies = {'http': "socks5://{}/".format(proxy), "https": "socks5://{}/".format(proxy)}
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    }

    res = True
    try:
        request = requests.get(url='https://www.{}.com'.format(web), headers=header, proxies=proxies, timeout=3)
        if request.status_code == 200:
            res = False
    except ValueError:
        Eprint("缺少pysocks库，请pip安装")
        sys.exit()
    except:
        res = True
    return res

def ReIp(res):
    global ip_ports
    ip_ports += re.findall(r"icp:a,id:\"(.*?)\"", res)

def SaveIpPortToTxt():
    with open("{}".format(outpath), "w")as f:
        f.write('\n'.join(ip_ports))
    # print(ip_ports)
    print("[*]爬取代理完成，已保存到{}".format(outpath))
def GetCookieFromTxt():
    with open("cookie.txt", "r") as f:
        a = f.read()
        if not a:
            return "fake"
        else:
            return a

def ChooseUrl(i):
    base_query = 'protocol=="socks5" && "Version:5 Method:No Authentication(0x00)"'


    extra_query = ' && country="CN" && after="{}" && before="{}"'.format(after, before)
    query = base_query + extra_query
    print("[*]query:{}".format(query))
    url = 'https://fofa.so/result?qbase64='+str(base64.b64encode(query.encode(encoding='utf-8')), 'utf-8')+'&page={}&page_size=10'.format(i)
    return url

def GetPxByFofa():
    # 最后再考虑获取国外代理需不需要把国家定位到国外。
    # if where == "df":
    try:
        if cookie == "fake":
            i = 1
            fofa_url = ChooseUrl(i)
            res = requests.get(url=fofa_url, headers=headernocookie, timeout=10)
            print("[*]第1页请求状态码:{}".format(res.status_code))
            if(res.status_code != 200):
                Eprint("[*]请检查网络哟")
                sys.exit()
            ReIp(res.text)
        else:
            # 一会需要加上对于cookie是否过期的判断。
            for i in range(1, page+1):
                fofa_url = ChooseUrl(i)
                res = requests.get(url=fofa_url, headers=headerwithcookie, timeout=10)
                if "返回上一页" in res.text:
                    Eprint("[*]cookie失效，或者你自定义爬取页数超出了你被允许访问的页数,请自行检查.")
                    CheckAllEffectiveness()
                    return
                print("[*]第{}页请求状态码:{}".format(i, res.status_code))
                if(res.status_code != 200):
                    Eprint("[*]请检查网络哟")
                    sys.exit()
                ReIp(res.text)
                time.sleep(5)
    except Exception as e:
        Eprint("[*]网络有问题，请检查")
        Eprint("[*]异常信息为:", end='')
        Eprint(e)
        sys.exit()

    CheckAllEffectiveness()

def Check(target, ip_port):
    if re.search('[a-zA-Z]]', ip_port):
        ip_ports.remove(ip_port)
        return
    if CheckEffectiveness(ip_port, target):
        ip_ports.remove(ip_port)
        print('[*]{}不行'.format(ip_port))
        return
    print('[*]{}行'.format(ip_port))
def CheckAllEffectiveness():
    global ip_ports
    # 检查有效性
    print("[*]检查代理可用性")
    threads = []
    if foreign:
        for i in range(len(ip_ports) - 1, -1, -1):
            ip_port = ip_ports[i]
            t = threading.Thread(target=Check, args=("google", ip_port))
            threads.append(t)
            t.start()
    else:
        for i in range(len(ip_ports) - 1, -1, -1):
            ip_port = ip_ports[i]
            t = threading.Thread(target=Check, args=("baidu", ip_port))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()
    print("[*]fofa爬取，一共找到{}个有效代理".format(len(ip_ports)))
    if len(ip_ports) == 0:
        Eprint("请重新圈定爬取代理的范围，此次没有爬取到可用代理。")
        sys.exit()

def GetOneEffectIpPort():
    global ip_ports
    if ip_ports:
        ip_port = ip_ports[0]
        ip = str(ip_port.split(":")[0])
        port = int(ip_port.split(":")[1])
        return ip, port
    else:
        Eprint("代理池没代理了")
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
            Eprint("[*]错误信息：", end='')
            Eprint(e)
            Eprint("[*] close")
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

def Banner():
    print(
        '''\033[32m

    ████████╗██╗   ██╗███╗   ██╗███╗   ██╗███████╗██╗     ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗
    ╚══██╔══╝██║   ██║████╗  ██║████╗  ██║██╔════╝██║     ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝
       ██║   ██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██║     ██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝
       ██║   ██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██║     ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝
       ██║   ╚██████╔╝██║ ╚████║██║ ╚████║███████╗███████╗██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║
       ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
                                                                            author : Gungnir  
                                                                            email：502591592@qq.com
        \033[0m'''
    )

def Parser():
    parser = argparse.ArgumentParser(description='''
          (￢︿̫̿￢☆)，哼，可恶! 竟然发现我了.
           (ˉ▽￣～)   既然发现我了，那就给你吧！
          ''')
    parser.add_argument("-a", "--after", help='时间范围搜索socks5代理，某时间之后，格式 2021-10-25 10:00:00，如果有具体时间，需要加引号', dest="after")
    parser.add_argument("-b", "--before", help='时间范围搜索socks5代理，某时间之前，格式 2021-10-25 10:00:00，如果有具体时间，需要加引号',
                        dest="before")
    parser.add_argument("-c", "--cookie", help='先去fofa登录，把cookie复制下来，不然只能请求一页代理，代理池会很小', dest="cookie")
    parser.add_argument("-f", "--foreign", help="爬取国外的代理",action="store_true" , dest="foreign")
    parser.add_argument("-o", "--out", help="有效代理输出文件位置（绝对路径，并附带自定义文件名）,默认当前文件夹下proxy.txt文件", type=str, dest="outpath")
    parser.add_argument("--page", help="要爬取多少页（默认为5，爬取越多，速度越慢），当然，最终能爬多少取决于你是否为会员。", type=int, dest="page")
    parser.add_argument("--no", help="不监听模式，只爬取代理，并将有效代理记录下来。", action="store_true", dest="nolisten")
    parser.add_argument("-p", "--port", help="监听端口", type=int,dest="port")
    args = parser.parse_args()
    options = vars(args)
    return options

def _init():
    # mode为0，爬取代理并监听
    # mode为1，爬取代理不监听
    # where为是爬取国内或者国外的代理,参数为f，d，df
    global nodatatime, headerwithcookie, headernocookie, after, before, cookie, mode, port, host, foreign, where, ip_ports, page, outpath

    # 初始化
    foreign = False
    nodatatime = 3
    mode = 0
    port = 9870
    host = "127.0.0.1"
    # where = "df"
    page = 5
    ip_ports = []
    outpath = "proxy.txt"

    # 默认从一天前到目前时间
    after = datetime.date.today() - datetime.timedelta(days=1)
    before = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')



    headernocookie = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    }

    options = Parser()

    if options['after']:
        after = options['after']
    if options['before']:
        before = options['before']

    if options['foreign']:
        foreign = True
    if options['port']:
        port = options['port']
    # 对用户的要求进行判断
    if options['nolisten']:
        mode = 1
    if options['page']:
        page = options['page']
    if options['outpath']:
        outpath = options['outpath']

    if not options['cookie']:
        cookie = GetCookieFromTxt()
        if cookie == "fake":
            return
        else:
            headerwithcookie = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
                'Cookie': cookie
            }
            return
    cookie = options['cookie']
    headerwithcookie = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        'Cookie': cookie
    }
def Run():
    # global host, port
    if foreign:
        print("[*]寻找国外可用代理")
        # where = 'f'
    else:
        print("[*]寻找可用代理")

    GetPxByFofa()
    SaveIpPortToTxt()


    if mode == 1:
        sys.exit()

    sever = socket.socket()
    # host = "127.0.0.1"
    # port = 9870
    sever.bind((host, port))

    sever.listen(20)

    print("[*] Listening Port {} ...".format(port))

    while True:
        try:
            conn, addr = sever.accept()
            thread = MyThread()
            thread.run(conn, addr)
            if thread.exitcode != 0:
                print("bye~")
                sys.exit()
        except KeyboardInterrupt:
            Eprint("用户退出")
            sys.exit()
        except:
            print("[*] connect from client error")


if __name__ == "__main__":
    Banner()
    _init()
    Run()