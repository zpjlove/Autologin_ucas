import gzip
import re
import http.cookiejar
import urllib.request
import urllib.parse
import xlrd
import time
import random
import ucas
userIndex = ''
"""
Function name :open_excel
Description :open the .xlsx file
Input :file,the file path
Output : the data of .xlsx file
Return : data
"""
def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print (str(e))
"""
Function name :excel_table_byindex
Description : open the .xlsx file from the given row and column
Input :file,the file path
        start, the beginning of column
        index, the beginning of row
Output : the data from the excel
Return : data,the data from the given row and column
"""

def excel_table_byindex(file,start, index = 0):
    data = open_excel(file)
    table = data.sheets()[index]
    nrows = table.nrows
    num = []
    for nrows in range(0,nrows):
        num.append(table.cell(nrows,start).value)
    return num

"""
Function name :ungzip
Description : decompress the data
Input :data, the data need to be decompressed
Output : the decompressed data
Return : data

"""
def ungzip(data):
    try:
        #print('正在解压.....')
        data = gzip.decompress(data)
        #print('解压完毕!')
    except:
        pass
        #print('未经压缩, 无需解压')
    return data
def getUserInfo(data):
    maxFlow_pattern = r'"maxFlow":.*?,'
    strlist = re.findall(maxFlow_pattern, data)
    stringlist = strlist[0]
    maxFlow = stringlist[10:-1]
    userName_pattern = r'"userName":.*?,'
    strlist = re.findall(userName_pattern, data)
    stringlist = strlist[0]
    userName = stringlist[12:-2]
    userId_pattern = r'"userId":.*?,'
    strlist = re.findall(userId_pattern, data)
    stringlist = strlist[0]
    userId = stringlist[10:-2]
    if(maxFlow == 'null'):
        maxFlow = '10240MB'
    return userName,userId,maxFlow

# 获取_querystring
"""
Function name :getqueryString
Description : get the querystring of url
Input :data, the data include the querystring
Output : the querystring
Return : querystring

"""
def getqueryString(data):
    pattern = r'wlanuserip.*?"'
    strlist = re.findall(pattern,data)
    stringlist = strlist[0]
    stringlist = stringlist[:-1]
    querystring = urllib.parse.quote(stringlist) #querystring need to be coding twice
    return querystring

"""
Function name :getuserIndex
Description : get the userindex of url
Input :data, the data include the userIndex
Output : the userIndex
Return : userIndex

"""
def getuserIndex(data):
    pattern = r'"userIndex":".*?"'
    strlist = re.findall(pattern,data)
    stringlist = strlist[0]
    userIndex = stringlist[13:-1]

    return userIndex

"""
Function name :getOpener
Description : constructed the header file
Input : head,the content of header file
Output : the constructed header file
Return : opener

"""
def getOpener(head):
    # 设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie
    cj = http.cookiejar.CookieJar()
    pro = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(pro)
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener

"""
Function name :isSuccess
Description : to judge the state of login
Input : data, the data of url after login
Output : the state of login
Return : stateFlag,if login successfully return ture else reture false

"""
def isSuccess(data):
    stateFlag = False
    pattern = r'success'
    strlist = re.findall(pattern, data)
    #strlist = strlist[0]
    if (len(strlist)):
        stateFlag = True
    return stateFlag


def isError(data):
    state = False
    pattern = r'用户不存在或密码错误'
    strlist = re.findall(pattern, data)
    #strlist = strlist[0]
    if (len(strlist)):
        state = True
        return state
    else:
        return state
"""
Function name :login
Description : autologin the landing page of ucas
Input : userInfo_url,the url include the user information
        login_url, the url of login
Output : the state of login(sucess of failed),the userIndex
Return : stateFlag,userIndex

"""
def login(userInfo_url, login_url, header, password, id, userIndex=None):
    #userIndex=''
    stateFlag = False
    opener = getOpener(header)
    op = opener.open(userInfo_url)
    data = op.read()
    querystring = getqueryString(data.decode())
    login_postDict = {
        # 特有数据，不同网站可能不同
        'service': '',
        'password': password,
        'userId': id,
        'operatorPwd': '',
        'vaildcode': '',

        'queryString': querystring
    }
    login_postData = urllib.parse.urlencode(login_postDict).encode()
    op = opener.open(login_url,login_postData)
    login_data = op.read()
    login_data = ungzip(login_data)
    decode_data = login_data.decode()
    infoopener = getOpener(header)
    infoop = opener.open(userInfo_url)
    infodata = infoop.read()
    userName, userId, maxFlow = getUserInfo(infodata.decode())
    if(isSuccess(decode_data)):
        userIndex = getuserIndex(decode_data)
        stateFlag = True
        return stateFlag,userIndex,maxFlow,userName,userId

    else:
        return stateFlag,userIndex
"""
Function name :logout
Description : autologout the logout page of ucas
Input : userIndex,the user information on the url
        logout_url, the url of logout
Output : the state of logout(sucess of failed)
Return : stateFlag

"""

def logout(userIndex,logout_url,header):
    stateFlag = False
    opener = getOpener(header)
    logout_postDict = {
        'userIndex': userIndex
    }
    logout_postData = urllib.parse.urlencode(logout_postDict).encode()
    op = opener.open(logout_url,logout_postData)
    logout_data = op.read()
    logout_data = ungzip(logout_data)
    decode_data = logout_data.decode()
    if(isSuccess(decode_data)):
        stateFlag = True
        return stateFlag
    else:
        return stateFlag

"""
Function name :wait
Description : when login successfully, wait certain seconds to check the state of login,calculate the next waited time
Input : second,the waited time
Output : the next waited time
Return : second

"""

def wait(second):
     time.sleep(second)
     second = pow(second,2)
     return second



def autologin():
    header = {
        'Connection': 'keep-alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x84_64; rv:49.0) like Gecko',
        'Accept-Encoding': 'gzip, deflate',
        'Host': '210.77.16.21',
        'Uprade-Insecure-Requests': '1'
    }
    userInfo_url = 'http://210.77.16.21/eportal//InterFace.do?method=getOnlineUserInfo'
    login_url = 'http://210.77.16.21//eportal/InterFace.do?method=login'


    password = 'freedom'
    id = []

    col = 0  # the column of id

    student_id = excel_table_byindex("id.xlsx",col)
    second = 2
    random_num = random.randint(0,len(student_id))
    id = student_id[random_num]

    login_state,userIndex,maxFlow,userName,userId = login(userInfo_url,login_url,header,password,id)
    if(login_state):
        print("登陆成功")
        str = "登录成功\n"+userName+"，您好\n"+"您剩余流量 "+maxFlow+"\n"
        return str

        #print("欢迎"+id)
        second = wait(second)
        #print(second)
    else:

        print("登陆失败")
        str = "登录失败"
        return str
        #print("重新登陆")
        random_num = random.randint(0, len(student_id))
        id = student_id[random_num]
        second = 0
        print(second)





def autologout():
    header = {
        'Connection': 'keep-alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x84_64; rv:49.0) like Gecko',
        'Accept-Encoding': 'gzip, deflate',
        'Host': '210.77.16.21',
        'Uprade-Insecure-Requests': '1'
    }
    logout_url = 'http://210.77.16.21//eportal/InterFace.do?method=logout'
    """
    if(userIndex == ''):
        str = "您未在线，请登录！"
        return str
    """
    logout_state = logout(userIndex,logout_url,header)
    if(logout_state):
        print("注销成功")
        str = "注销成功\n"+"感谢您的使用！"
        return str
    else:
        print("注销失败")
        str = "注销失败"
        return str



