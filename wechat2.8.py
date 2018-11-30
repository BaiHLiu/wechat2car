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
from aip import AipFace
import base64
import shutil

list_str=[]
#初始化wxpy
bot = Bot(console_qr=True,cache_path=True)
#bot = Bot(cache_path=True)
bot.groups(update=True, contact_only=False)
group_name=bot.groups().search('潍水人家')    #指定监听的群聊
#接收图片
@bot.register(chats=group_name)
@bot.register(Friend,PICTURE)

def user_msg(msg):     #定义一个接收消息的函数
    image_name = msg.file_name
    friend = msg.chat
    print(msg.chat)
    print('接收图片')
    msg.get_file(''+msg.file_name)


    #百度api车型识别参数初始化
    APP_ID_type = '11688197'
    API_KEY_type = 'hTfKPPNo7BgxA3tSlq17IxbI'
    SECRET_KEY_type = '3gP3ZU9n19XtvyA99U0Aa8Or1AlGtMHp'
    type_client = AipImageClassify(APP_ID_type,API_KEY_type,SECRET_KEY_type)

    #百度api车牌识别参数初始化
    APP_ID_number = '11689666'
    API_KEY_number = 'pks4e2P2Zcks12pHzzSOmYDF'
    SECRET_KEY_number = 'XRk451xO8iyVPAbGKXIs51plbx6Rx4m7'
    number_client = AipOcr(APP_ID_number,API_KEY_number,SECRET_KEY_number)

    #百度api人脸识别参数初始化
    APP_ID = '14333678'
    API_KEY = 'WWUtFk8qzH2CgtaGIBwGGAHT'
    SECRET_KEY = 'UOzEyLvphtwP6q49TuHjxX7Gd2lo50GG'
    face_client = AipFace(APP_ID, API_KEY, SECRET_KEY)


    #读取图片
    def file_extension(path):           #定义一个取文件扩展名的函数
        return os.path.splitext(path)[1]
    rootdir = os.path.dirname(os.path.realpath(__file__))  #获取当前路径
    all_file = os.listdir(rootdir) #列出文件夹下所有的目录与文件
    for file in all_file:     #遍历所有文件
        if file_extension(file)=='.py':    #此次用来判断是否为用户发来的图片文件
            continue                       #经测试Linux下使用=='.png'会有问题，未知原因
        if file_extension(file)=='.out':
            continue
            os.remove(file)
        if file_extension(file)=='.pkl':
            continue
        if file_extension(file)=='.gif':
            continue
            os.remove(file)
        if file_extension(file)=='.docx':
            continue
            os.remove(file)
        if file_extension(file)=='.xlsx':
            continue
            os.remove(file)
        if file_extension(file)=='.doc':
            continue
            os.remove(file)
        if file_extension(file)=='.xls':
            continue
            os.remove(file)
        def get_file_content(file_Path):
            with open(file_Path,'rb') as fp:
                    return fp.read()
        image = get_file_content(file)

        #调用百度api车型识别
        car_type_result = type_client.carDetect(image,options = {'top_num':1})['result'][0]['name']
        print(car_type_result)
        #调用百度api植物识别
        flower_type_result = type_client.plantDetect(image)['result'][0]['name']
        #调用百度api人脸识别
        with open(file,"rb") as f:  
            face_image = str(base64.b64encode(f.read()),'utf-8')
            face_imageType = "BASE64"
            options = {}
            options["face_field"] = "age,beauty,gender"
            face_result_origin = face_client.detect(face_image,face_imageType,options)
        

        if car_type_result == '非车类':
            if flower_type_result =='非植物':
                if str(face_result_origin['result']) == 'None':   #用户发来了一张无关的照片
                    os.remove(file)
                else:
                    if face_result_origin['result']['face_num'] >1:
                        print('不支持处理多张人脸！！')
                    else:
                        msg.reply('成功接收图片，正在识别...\n*本消息由服务器自动发出，若不慎打扰请谅解')
                        age = (str(face_result_origin['result']['face_list'][0]['age'])+'岁')
                        gender = str((face_result_origin['result']['face_list'][0]['gender'])['type'])
                        beauty = str('%.2f'%(face_result_origin['result']['face_list'][0]['beauty']))
                        print(face_result_origin)
                        msg.reply('--------识别结果--------'+'\n年龄:'+age+'\n性别:'+gender+'\n美度:'+beauty+'\n*本消息由服务器自动发出，若不慎打扰请谅解')
                        shutil.move(file,'/home/python/processed/face')
                        #os.remove(file)
            else:
                msg.reply('成功接收图片，正在识别...\n*本消息由服务器自动发出，若不慎打扰请谅解')
                print(flower_type_result)
                score = type_client.plantDetect(image)['result'][0]['score']*100
                flower_type_score = '%.2f' % score
                message_all = '--------识别结果--------'+'\n植物名称:'+flower_type_result+'\n相似度:'+flower_type_score+'%\n*本消息由服务器自动发出，若不慎打扰请谅解'
                msg.reply(message_all)
                os.remove(file)
        else:
            msg.reply('成功接收图片，正在识别...\n*本消息由服务器自动发出，若不慎打扰请谅解')
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
                ori = number_client.licensePlate(image)
                err = str('error_code'in ori)
                if err == 'True':
                    car_number_result = '未检测到车牌'
                    print(car_number_result)
                else:
                    car_number_result = number_client.licensePlate(image)['words_result']['number']
                    print(car_number_result)
               
                print(type(car_number_result))
                print(type(car_type_result))
                print(type(avg_price_str))
                message_all = '--------识别结果--------'+'\n车型:'+car_type_result+'\n车牌号:'+car_number_result+'\n参考价格'+avg_price_str+'万元'+'\n详细信息:'+url+'\n*本消息由服务器自动发出，若不慎打扰请谅解'
                print(message_all)
                msg.reply(message_all)
        os.remove(file)
bot.join()

