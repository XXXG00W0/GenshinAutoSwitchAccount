from pymouse import PyMouse
from pykeyboard import PyKeyboard
import os, time, random, win32api, win32con, win32gui, win32ui
import win32com.client
import ctypes, sys, pandas

user32dll = ctypes.windll.LoadLibrary ("C:\\Windows\\System32\\user32.dll")

logOutPos = (1950, 1050)
logoutCheckYesButtonPos = (1150, 590)
accountPos = (1024, 400)
passwordPos = (1024, 530)
agreementCheckPos = (710, 660)
logInPos = (1024, 740)

MOUSE_LEFT=0
MOUSE_MID=1
MOUSE_RIGHT=2

m = PyMouse()
kb = PyKeyboard()


def changeLanguage(hwnd, lang="EN"):
    """
    切换语言（原作者：https://zhuanlan.zhihu.com/p/374077032）
    :param lang: EN––English; ZH––Chinese
    :return: bool
    """
    LANG = {
        "ZH": 0x0804,
        "EN": 0x0409
    }
    print(hwnd)
    language = LANG[lang]
    result = win32api.SendMessage(
        hwnd,
        win32con.WM_INPUTLANGCHANGEREQUEST,
        0,
        language
    )
    if not result:
        return True

# def switchWindow():
#     kb.press_key(kb.alt_key)
#     for i in range(3):
#         kb.press_key(kb.tab_key)
#         time.sleep(0.1)
#         kb.release_key(kb.tab_key)
#     kb.release_key(kb.alt_key)


def isAdmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def selectAll():
    kb.press_key(kb.control_key)
    kb.tap_key('a')
    kb.release_key(kb.control_key)


def getCurrentWindow(windowName):
    hwnd = win32gui.FindWindow(None, windowName)
    return hwnd


def getCurrentWindowRect(hwnd):
    genshinWindowRect = win32gui.GetWindowRect(hwnd)
    print(genshinWindowRect)


def setWindowForeground(hwnd):
    user32dll.SwitchToThisWindow(hwnd, True)


def readPasswordFile(path):
    passwordDict = pandas.read_csv(path, header=None, index_col=0).to_dict()[1]
    return list(passwordDict.items())


def main():
    # 查询是否以管理员权限启动（原作者：https://blog.csdn.net/MemoryD/article/details/83148305）
    if not isAdmin():
        print("未使用管理员权限运行")
        # 请求管理员权限
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    # 抓取原神窗口
    while True:
        genshinWindowName = '原神'
        genshinHwnd = getCurrentWindow(genshinWindowName)
        if genshinHwnd == 0:
            print(f"{genshinHwnd} 原神应用未找到")
            input("按任意键重新尝试")
        else:
            print(f'原神程序指针：{genshinHwnd}')
            break

    # 读取账密csv文件
    pswdList = readPasswordFile('原神账密.csv')
    if len(pswdList) == 0:
        print(f'当前账密文件为空，请以 <手机号码>,<密码> 为一行添加账密')
        return
    print('账号密码如下：')
    for i in range(1, len(pswdList)+1):
        print(f'{i}\t{pswdList[i-1][0]}\t{pswdList[i-1][1]}')
        
    # 询问账号索引，若索引错误则重新询问
    while 1:
        try:
            accountIndex = int(input('输入需要切换的账号索引：'))
            account, password = pswdList[accountIndex-1]
            print(f'选定账户\'{account}\'及密码\'{password}\'')
        except IndexError:
            print(f'输入的索引"{accountIndex}"不存在')
        except ValueError:
            print(f'"{accountIndex}"不是有效值')
        else:
            break

    # 切换到原神窗口
    setWindowForeground(genshinHwnd)    
    time.sleep(1)
    # 切换输入法语言为英语
    changeLanguage(genshinHwnd, 'EN')   
    time.sleep(1)
    # 右下角点击登出按钮
    m.click(logOutPos[0], logOutPos[1]) 
    time.sleep(1)
    # 登出窗口点击确认
    m.click(logoutCheckYesButtonPos[0], logoutCheckYesButtonPos[1]) 
    time.sleep(1)
    setWindowForeground(genshinHwnd)
    # 点击账号输入框
    m.click(accountPos[0], accountPos[1])   
    time.sleep(1)
    selectAll()
    # 输入手机号/邮箱
    kb.type_string(str(account))
    time.sleep(1)
    # 点击密码输入框
    m.click(passwordPos[0], passwordPos[1])
    time.sleep(1)
    # 输入密码
    kb.type_string(password)
    time.sleep(1)
    # 点击同意用户协议和隐私政策
    m.click(agreementCheckPos[0], agreementCheckPos[1])
    time.sleep(1)
    # 点击进入游戏
    m.click(logInPos[0], logInPos[1])
    time.sleep(1)
    # 切换输入法语言为中文
    changeLanguage(genshinHwnd, 'ZH')
    time.sleep(8)
    # 点击登入游戏
    m.click(logInPos[0], logInPos[1])


if __name__ == '__main__':
    main()
