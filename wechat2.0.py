#-*-coding:utf-8-*-
from aip import AipImageClassify
import os.path
from aip import AipOcr
from urllib import request
from bs4 import BeautifulSoup
from urllib.parse import quote
import string
import numpy as np
import os
from wxpy import *

list_str=[]
#初始化wxpy
bot = Bot()
#接收图片
@bot.register(Friend,PICTURE)
def user_msg(msg):
    image_name = msg.file_name
    friend = msg.chat
    print(msg.chat)
    print('接收图片')
    msg.get_file(''+msg.file_name)


    #百度api车型识别参数初始化（具体请移步ai.baidu.com）
    APP_ID_type = ''
    API_KEY_type = ''
    SECRET_KEY_type = ''
    client_type = AipImageClassify(APP_ID_type,API_KEY_type,SECRET_KEY_type)

    #百度api车牌识别参数初始化（具体请移步ai.baidu.com）
    APP_ID_number = ''
    API_KEY_number = ''
    SECRET_KEY_number = ''
    client = AipOcr(APP_ID_number,API_KEY_number,SECRET_KEY_number)


    #读取图片
    def file_extension(path):           #定义一个取文件扩展名的函数
      return os.path.splitext(path)[1]
    rootdir = os.path.dirname(os.path.realpath(__file__))  #获取当前路径
    all_file = os.listdir(rootdir) #列出文件夹下所有的目录与文件
    for file in all_file:     #遍历所有文件
        if file_extension(file)=='.py':
            continue    #剔除本身的脚本文件
        def get_file_content(file_Path):
            with open(file_Path,'rb') as fp:
                    return fp.read()
        image = get_file_content(file)


        #调用百度api车型识别
        car_type_result = client_type.carDetect(image,options = {'top_num':1})['result'][0]['name']
        print(car_type_result)

        if car_type_result == '非车类':     #判断是否是需要处理的车的照片
            os.remove(file)
        else:

            #使用爬虫从汽车大全查找该车型价格
            url = quote('http://sou.qichedaquan.com/qiche/'+car_type_result, safe=string.printable)
            #print(url)
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
            page = request.Request(url, headers=headers)
            page_info = request.urlopen(page).read()
            page_info = page_info.decode('utf-8')

            soup = BeautifulSoup(page_info, 'html.parser')
            #print(soup)
            title = soup.find('p','dealer_price')
            price = str(soup.find('em'))
            
            if price == 'None':   #判断汽车大全网是否有该车型的信息
                avg_price = 'Unkonwn'
                print(avg_price)
            else:
                price = ''.join(price.split())    #去除空格
                min_price_list = []
                a = 0
                b = 0
                for word in price:
                    a = a+1
                    if word == '>':
                        break
                for word in price:
                    b = b+1
                    if word == '-':
                        break
                c1 = a+1    #获取最低价第一个数字在字符串中的索引位置
                c2 = b-1    #获取最低价最后一个数字在字符串中的索引位置
                i = 0
                for word1 in price:
                    i = i+1
                    if i >= c1:
                        min_price_list.append(word1)
                    else:
                        continue
                    if i >= c2:
                        break

                min_price = float(''.join(min_price_list))   #list转换float
                #min_price = np.float64(min_price_list)
                #print(min_price)

                max_price_list = []
                a = 0
                b = 0
                for word in price:
                    a = a+1
                    if word == '-':
                        break
                for word in price:
                    b = b+1
                    if word == '/':
                        break
                c1 = a+1    #获取最高价第一个数字在字符串中的索引位置
                c2 = b-3    #获取最高价最后一个数字在字符串中的索引位置
                i = 0
                for word1 in price:
                    i = i+1
                    if i >= c1:
                        max_price_list.append(word1)
                    else:
                        continue
                    if i >= c2:
                        break
                max_price = float(''.join(max_price_list))   #list转换float
                #max_price = np.float64(max_price_list)
                #print(max_price)

                avg_price = round((min_price + max_price)/2.0,2)     #获取该车型平均价格
                print('平均价格:',avg_price,'万元')
                avg_price_str = str(avg_price)


                #调用百度api车牌识别
                ori = client.licensePlate(image)
                err = str('error_code'in ori)
                if err == 'True':
                    car_number_result = '未检测到车牌'
                    print(car_number_result)
                else:
                    car_number_result = client.licensePlate(image)['words_result']['number']
                    print(car_number_result)
               
                print(type(car_number_result))
                print(type(car_type_result))
                print(type(avg_price_str))
                message_all = '--------识别结果--------'+'\n车型:'+car_type_result+'\n车牌号:'+car_number_result+'\n参考价格'+avg_price_str
                print(message_all)
                

                #print(car_number_result,car_type_result,avg_price)
                #print('----------------------------------')

                #msg.reply('【本消息由机器自动发出，请勿回复】识别成功！！')
                msg.reply(message_all)
                os.remove(file)
bot.join()
            
