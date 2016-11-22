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
import string


index = '''http://www.xmsmjk.com'''
date = "2016-11-23"
dateformat = "11/23"
prefertime = "9:00"

mailto_list=['xxxx@163.com']
mail_host="smtp.163.com"  #设置服务器
mail_user="xxxx"    #用户名
mail_pass="xxxxx"   #口令
mail_postfix="163.com"  #发件箱的后缀

def GetBookUrl():
    global  date
    global  index
    if date  == "":
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    temp = '/UrpOnline/Home/Index/2_1030120_%s___'%date
    #temp = '/UrpOnline/Home/Index/2_2030000_%s___' % date #test
    ret = dict()
    value = {'orgId':'2',
            'deptCode':'1030120',
            #'deptCode':'2030000',# test
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
        experts = soup.select('div[class=expert_div_index]')#each experts
        for expert in experts:
            #get the expert information
            expertname = expert.select('a[class=index_top_in_name]')[0].contents[0]
            #parse the time information
            divs = expert.select('div[class=div_index_bottom]')
            for div in divs :
                #tagas = div.find_all(name='a')
                tagas = div.select('a')
                for taga in tagas:
                    key = index + taga.get('href')
                    value = taga.contents
                    left = value[1].string
                    time_ = value[0]
                    if dateformat in time_:
                        '''here is the final address of the query
                        :key is the final address
                        time_ is the date
                        left is the left orders
                    '''
                        timelist = queryTime(key)
                        if len(timelist) != 0:
                            ret[expertname] = timelist
                        #ret[key] = time_ + left
                    else:
                        continue


    except uerror.HTTPError as e:
        print(e.reason)
    finally:
        return ret


def queryTime(url):
    timelist = list()
    try:
        req = ur.Request(url)
        response = ur.urlopen(req)
        soup = bs(response.read().decode('utf-8'),"html.parser")
        divs = soup.select("div[class=dateSpan]")
        for div in divs:
            tagas = div.select('a')
            for taga in tagas:
                duration = taga.contents[0]
                time = duration.split('-')
                start = time[0]
                end = time[1]
                if strTimeComp(prefertime,end) == 1:
                    timelist.append(start +'-'+end +'\r\n')
    except uerror.HTTPError as e:
        print(e.reason)
    finally:
        return timelist


def strTimeComp(mytime,comtime):
    '''
    :param mytime: format xx:xx
    :param comtime: format xx:xx
    :return: 0-equal 1= more 2- less
    '''
    myhour = int(mytime.split(':')[0])
    mymin = int(mytime.split(':')[1])

    comhour = int(comtime.split(':')[0])
    commin = int(comtime.split(':')[1])

    if myhour > comhour:
        return 1
    if myhour < comhour:
        return 2
    if myhour == comhour and mymin > commin:
        return 1
    if myhour == comhour and mymin < commin:
        return 2

    if myhour == comhour and mymin == commin:
        return 0


def FormatContent(urldict):
    if urldict == None or type(urldict) != type(dict()) or len(urldict) == 0 :
        return  False

    content = str()
    content += date +':\r\n'
    for item in urldict:
        content += '    '+item +":\r\n"
        for stamp in urldict[item]:
            content += "        "+stamp+'\r\n'
        '''
        temp = urldict[item].split('|')
        day = temp[0]
        left = temp[1]
        content += day+" 剩余:%s\r\n"%left
        '''
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
        #print(result)
        if result != False:
            print("Got order")
            SendMailNotify(result,"第一医院产科可预约");
            break;
        time.sleep(1)






