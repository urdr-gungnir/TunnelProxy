# TunnelProxy

是一个本地隧道代理，可以从fofa爬取免费的socks代理，然后构建代理池，如果一个代理失效，会自动切换。

现在也可以当作获取免费代理的工具。

由于fofa原因，现在fofa试运行的域名，并不能直接搜索，需要有会员才能使用，所以有fofa_key，此工具还能使用，-A参数。

而如果没有会员，想像之前cookie获取的已经不能使用了。。。需要等fofa稳定之后，才可以。

## 应用场景

1.渗透测试需要访问某些国内网站（比如edu的），想要隐藏自己，但是国外代理不能访问，也没有稳定的可用代理的时候。

2.临时对于科学上网有需求，需要国外代理，可以使用工具获得。

## Need

```
python3
pip install -r requirements.txt
```

## ParameterList

![Snipaste_2021-12-31_18-23-51](https://user-images.githubusercontent.com/73213935/147818127-2aeedc21-184b-458e-a2b0-77f8826e2fc7.png)


## HowToUse

~~在运行之前，建议先去fofa登录，拿到cookie，因为fofa登陆过后，能爬取很多页，能得到更多白嫖的代理。（在登陆的时候选择保持登录，可以使cookie长时间有效，不用来回换。~~

更新了可以使用api，把自己的key和email填在config.conf文件中，使用

```
python TunnelProxy.py -A
```


默认还是cookie，需要用-A选项才是用api。

下面是拿cookie方法，适合我们这种穷人。

![image](https://github.com/urdr-gungnir/TunnelProxy/blob/main/img/Snipaste_2021-10-26_22-36-39.png)

复制之后，可以选择把cookie放置在cookie.txt中, TunnelProxy会自动读取，之后就不用在命令行中使用 -c参数了。

或者运行

```
python TunnelProxy.py -c You-Cookie
```

![image](https://github.com/urdr-gungnir/TunnelProxy/blob/main/img/Snipaste_2021-10-26_22-24-04.png)

默认爬取的代理时间为前一天到现在的时间的。

如果爬取效果不理想，可以通过-a和-b来调整时间，建议不用改，默认的时间大部分情况是最好的。

时间样例：2021-10-25 10:00:00

```
python TunnelProxy.py -a "2021-10-25 10:00:00" -b "2021-10-26" -c You-Cookie
```

有时候我们不想要直接运行代理，而是为了获取免费代理，这个时候我们可以使用 --no 参数，（不监听，只记录有效代理保存到本地）

在运行之后，等程序爬取完代理，找出可用代理，默认会监听本地9870端口。（如果想改变监听端口，可以使用 -p 自行改变port。）

等到程序监听9870端口，就可以配合浏览器插件SwitchyOmega，让他把浏览器流量都转发给本地9870端口，这时候，我们就可以愉快走着免费代理

![image](https://github.com/urdr-gungnir/TunnelProxy/blob/main/img/Snipaste_2021-10-26_22-50-04.png)



## 实在看不懂的话，我平时这样用

我把cookie都放在cookie.txt下

1. 需要在本地监听，访问外网

```
python .\TunnelProxy.py -f
```

2. 不需要本地监听，拿到国外代理

```
python .\TunnelProxy.py -f --no --page 2
```

3. 需要本地监听，访问国内网站

```
python .\TunnelProxy.py
```



## 自言自语

如果你觉得对你有用，请帮我点个star，有问题请提issue。

