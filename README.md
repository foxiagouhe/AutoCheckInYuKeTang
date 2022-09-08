### Auto Check In YuKeTang (ZCST)



#### 前言

**本脚本仅供学习交流，切勿用于其他用途**


雨课堂（长江）登陆时加了个腾讯防水墙验证，直接通过api登陆的方法很难。

这份源码采用的方案是使用selenium模拟滑动滑块，登陆后保存cookie作为下次登陆用。

雨课堂（长江）的cookie有效期为15天，可以通过一周更新一次cookie来维持登陆。

目前脚本部署在树莓派上可稳定自动签到。各位可以根据自己需求更改脚本以适应其他类型系统。

此脚本适用珠海科技学院。

> 测试环境：
>
> ```shell
> $ screenfetch
>          _,met$$$$$gg.           pi@raspbian
>       ,g$$$$$$$$$$$$$$$P.        OS: Debian GNU/Linux 10 (buster) aarch64 
>     ,g$$P""       """Y$$.".      Kernel: aarch64 Linux 5.10.78-Release-OPENFANS+20211111-v8
>    ,$$P'              `$$$.      Uptime: 20h 35m
>   ',$$P       ,ggs.     `$$b:    Packages: 1062
>   `d$$'     ,$P"'   .    $$$     Shell: zsh 5.7.1
>    $$P      d$'     ,    $$P     CPU: BCM2835 @ 4x 1.2GHz [37.0°C]
>    $$:      $$.   -    ,d$$'     GPU: BCM2708
>    $$\;      Y$b._   _,d$P'      RAM: 256MiB / 954MiB
>    Y$$.    `.`"Y$$$$P"'          Host: Raspberry Pi 3 Model B Rev 1.2
>    `$$b      "-.__              
>     `Y$$                        
>      `Y$$.                      
>        `$$b.                    
>          `Y$$b.                 
>             `"Y$b._             
>                 `""""     
> ```



#### 使用

##### 安装依赖

需要安装chromium和chromium-driver

```shell
sudo apt install chromium
sudo apt install chromium-driver
```

注意：不同Linux版本，chromium和chromium-driver的包名不一定相同



需要安装以下python包（以下标注的版本是测试环境使用的版本）：

```
numpy==1.23.2
opencv-python==4.3.0.36
requests==2.28.1
selenium==3.141.0
urllib3==1.26.12
```



##### 开始使用

###### 1. 编辑user.csv文件

csv文件结构：

- name：姓名
- user：登陆账号
- pwd：登陆密码
- type：登陆类型，手机号码登录为PP，邮箱为E
- apikey：server酱的key

一行一个用户填写好后，删除空行保存



###### 2. 获取cookie

```shell
python3 AutoCheckInYuKeTang/handleToken/main.py
```

屏幕将不会有回显，会在log文件夹下生成handleToken开头的log文件



###### 3. 开始签到

```shell
python3 AutoCheckInYuKeTang/attendYukeTang/AutoAttend.py
```

屏幕将不会有回显，会在log文件夹下生成姓名开头的log文件，一个用户对应一个log文件



##### 添加单个用户

由于cookie不是每天刷新，某天需要添加用户则需等待若干日，现在可以通过adduser.py文件来即时添加用户

编辑data目录下的adduser.csv文件，一行一个用户填写好后，删除空行保存

然后执行：

```shell
python3 AutoCheckInYuKeTang/handleToken/adduser.py
```



##### 高级使用

Linux使用crontab做定时执行

###### 自动执行签到

```
0 8 * * *  python3 /home/pi/AutoCheckInYuKeTang/attendYukeTang/AutoAttend.py /dev/null 2>&1
30 13 * * * python3 /home/pi/AutoCheckInYuKeTang/attendYukeTang/AutoAttend.py /dev/null 2>&1
30 18 * * *  python3 /home/pi/AutoCheckInYuKeTang/attendYukeTang/AutoAttend.py /dev/null 2>&1
```

每天的08:00、13:30、18:30执行自动签到脚本



###### 自动更新cookie

```
30 7 * * 7 python3 /home/pi/AutoCheckInYuKeTang/handleToken/main.py /dev/null 2>&1
```

每周日的07:30执行更新cookie



#### 其他

##### 文件结构

```shell
$ tree 
.
├── README.md
├── attendYukeTang
│   └── AutoAttend.py // 作用：自动签到
├── data
│   ├── adduser.csv // 作用：需要添加用户名单
│   ├── user.csv // 作用：用户名单
│   └── user_data.json // 作用：存储用户的cookie等信息给AutoAttend.py文件使用
├── handleToken
│   ├── TencentSlide.py // 作用：解决腾讯防水墙的核心功能
│   ├── adduser.py // 作用：添加当个用户
│   └── main.py // 获取cookie
└── log
    └── 2022-xx-xx // 日志输出

5 directories, 8 files
```



##### user_data.json 文件结构

```json
[
  {
    "name": "xxx",
    "user_id": 00000000,
    "cookie": {
      "domain": "",
      "expiry": 00000000,
      "httpOnly": true,
      "name": "sessionid",
      "path": "/",
      "sameSite": "None",
      "secure": true,
      "value": ""
    },
    "apikey": ""
  }
]
```



##### user.csv  & adduser.csv 文件结构

```csv
name,user,pwd,type,apikey
xxx,13455763876,123456,PP,xxxxx
xxx,example@mail.com,13245,E,xxxxxx
```



