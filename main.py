#coding=utf-8
import urllib.request as ur
import urllib.error as uerror
import urllib.parse as up
import time
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as bs
import ssl
import json


index = '''http://www.xmsmjk.com'''
date = "2016-10-21"

mailto_list=['@163.com']
mail_host="smtp.163.com"  #设置服务器
mail_user=""    #用户名
mail_pass=""   #口令
mail_postfix=".com"  #发件箱的后缀

def GetBookUrl():
    global  date
    global  index
    if date  == "":
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    temp = '/UrpOnline/Home/Index/2_1030120_%s___'%date
    ret = dict()
    value = {'orgId':'2',
            'deptCode':'1030120',
            'sex':'0',
            'page':'1',
            'orderType':'1',
            'orgType':'1',
            'strSta':temp,
            'date':date}

    data = up.urlencode(value).encode(encoding='utf-8')
    url = index +"/UrpOnline/Home/GetIndexList"
    req = ur.Request(url,data)
    try:
        response = ur.urlopen(req)
        soup = bs(response.read().decode('utf-8'),"html.parser")
        divs = soup.select('div[class=div_index_bottom]')
        for div in divs :
            div.select('a')
            #tagas = div.find_all(name='a')
            tagas = div.select('a')
            for taga in tagas:
                key = index + taga.get('href')
                value = taga.contents
                left = value[1].string
                time_ = value[0]
                ret[key]=time_+left

    except uerror.HTTPError as e:
        print(e.reason)
    finally:
        return ret



def FormatContent(urldict):
    if urldict == None or type(urldict) != type(dict):
        return  False

    content = str()
    for item in urldict:
        temp = urldict[item].split('|')
        day = temp[0]
        left = temp[1]
        content += day+" 剩余:%s\r\n"%left
    return content



def SendMailNotify(content,title):
    me = "hello" + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = title
    msg['From'] = me
    msg['To'] = ";".join(mailto_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, mailto_list, msg.as_string())
        server.close()
    except Exception as e:
        print(str(e))

if __name__ == "__main__" :
    while(True):
        result = FormatContent(GetBookUrl())
        print(result)
        if result != False:
            SendMailNotify(result,"第一医院产科可预约");
            break;






