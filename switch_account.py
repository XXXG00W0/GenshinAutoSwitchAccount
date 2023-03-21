from pymouse import PyMouse
from pykeyboard import PyKeyboard
import win32api, win32con, win32gui, win32ui
# import win32com.client keyboard, winsound
import ctypes, sys, pandas, json, time

user32dll = ctypes.windll.LoadLibrary("C:\\Windows\\System32\\user32.dll")

# 默认坐标配置留档
# coordCfg = {
#     'size': (2048, 1152),
#     'logOutPos': (1950, 1050),
#     'logoutCheckYesButtonPos': (1150, 590),
#     'accountPos': (1024, 400),
#     'passwordPos': (1024, 530),
#     'agreementCheckPos': (710, 660),
#     'logInPos': (1024, 740)
# }


MOUSE_LEFT = 0
MOUSE_MID = 1
MOUSE_RIGHT = 2

m = PyMouse()
kb = PyKeyboard()


def coordResize(coord, upperLeft):
    return round(upperLeft[0] + coord[0]), round(upperLeft[1] + coord[1])


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
    # print(hwnd)
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


def getWindow(windowName):
    return win32gui.FindWindow(None, windowName)


def getActiveWindow():
    return win32gui.GetActiveWindow()


def getWindowName(hwnd):
    return win32gui.GetWindowText(hwnd)


def getResolution():
    width = int(win32api.GetSystemMetrics(0))
    height = int(win32api.GetSystemMetrics(1))
    return width, height


def toggleFullScreen():
    kb.press_key(kb.alt_key)
    kb.tap_key(kb.enter_key)
    kb.release_key(kb.alt_key)


def getWindowRect(hwnd):
    windowRect = win32gui.GetWindowRect(hwnd)
    # print(windowRect)
    return windowRect


def setWindowForeground(hwnd):
    user32dll.SwitchToThisWindow(hwnd, True)


def readPasswordFile(path):
    passwordDict = pandas.read_csv(path, header=None, index_col=0).to_dict()[1]
    return list(passwordDict.items())


def readConfig(fileName):
    # 读取config.json文件（包含按钮和文本框的坐标）
    # https://blog.csdn.net/weixin_41287260/article/details/102472268
    # 首先要弄明白json库的四个方法：
    # dumps和loads、dump和load。
    # 其中，dumps和loads是在内存中转换（python对象和json字符串之间的转换），
    # 而dump和load则是对应于文件的处理
    try:
        with open('config.json') as cfgJson:
            cfg = json.load(cfgJson)
            return cfg
    except FileNotFoundError:
        print(f'\'config.json\'不存在')
        return


def writeConfig(cfg):
    with open('config.json', 'w') as cfgJson:
        json.dump(cfg, cfgJson)


def convertCoords(resolutionCfg):
    # 以新的屏幕尺寸为基准转换坐标
    width, height = getResolution()
    defaultCoordsCfg = resolutionCfg['default']
    defaultWidth, defaultHeight = defaultCoordsCfg['size']
    resize = lambda x, y: [int(round(x * width / defaultWidth)), int(round(y * height / defaultHeight))]
    newCoordCfg = {}
    for key, coord in defaultCoordsCfg.items():
        newCoordCfg[key] = resize(coord[0], coord[1])
    resolutionCfg[f'{width}*{height}'] = newCoordCfg
    return resolutionCfg


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
        genshinHwnd = getWindow(genshinWindowName)
        windowRect = getWindowRect(genshinHwnd)

        if genshinHwnd == 0:
            print(f"{genshinHwnd} 原神应用未找到")
            input("启动原神后按回车重试")
        else:
            print(f'原神程序指针：{genshinHwnd}')
            break

    cfg = readConfig('./config.json')
    if not cfg:
        return

    # # 读取账密csv文件（已弃用）
    # pswdList = readPasswordFile('原神账密.csv')

    # 从cfg字典中读取账密
    pswdList = list(cfg['account'].items())
    while len(pswdList) == 0:
        print(f'当前账密信息为空，现在添加账密')
        account = input('请输入账号：')
        pswd = input('请输入密码：')
        pswdList.append([account, pswd])
        cfg['account'][account] = pswd

    print('账号密码如下：')
    for i in range(1, len(pswdList) + 1):
        print(f'{i}\t{pswdList[i - 1][0]}\t{pswdList[i - 1][1]}')

    # 询问账号索引，若索引错误则重新询问
    while 1:
        try:
            accountIndex = input('输入需要切换的账号索引：')
            accountIndex = int(accountIndex)
            account, password = pswdList[accountIndex - 1]
            print(f'选定账户\'{account}\'及密码\'{password}\'')
        except IndexError:
            print(f'输入的索引"{accountIndex}"不存在')
        except ValueError:
            print(f'"{accountIndex}"不是有效值')
        else:
            break

    # 检测原神是否以全屏运行，否则切换至全屏
    if windowRect[0] < 0:
        # 仅适配16比9的屏幕，暂未适配其他比例的屏幕
        print(f'{genshinWindowName}以全屏运行')
        # 切换到原神窗口
        setWindowForeground(genshinHwnd)
        time.sleep(1)
    else:
        print(f'{genshinWindowName}以窗口化运行，将尝试切换至全屏')
        setWindowForeground(genshinHwnd)
        time.sleep(1)
        # win32gui.SetWindowPos(genshinHwnd, 0, 0, 0, 2048, 1152, 1)  Error: Permission Denied
        # https://learn.microsoft.com/en-us/windows/win32/api/control/nf-control-ivideowindow-setwindowposition
        toggleFullScreen()

    width, height = getResolution()
    print(f'屏幕尺寸是 {width}*{height}')
    if width / height != 16 / 9:
        print(f'仅适配16:9的屏幕')
        return
    elif f'{width}*{height}' not in cfg['resolution']:
        print(f'\'{width}*{height}\'不存在，将尝试转换')
        cfg['resolution'] = convertCoords(cfg['resolution'])
    coordCfg = cfg['resolution'][f'{width}*{height}']

    # 写入刚才添加的账密和坐标
    writeConfig(cfg)

    # 切换输入法语言为英语
    changeLanguage(genshinHwnd, 'EN')
    time.sleep(1)
    # 右下角点击登出按钮
    m.click(coordCfg['logOutPos'][0], coordCfg['logOutPos'][1])
    time.sleep(1)
    # 登出窗口点击确认
    m.click(coordCfg['logoutCheckYesButtonPos'][0], coordCfg['logoutCheckYesButtonPos'][1])
    time.sleep(1)
    setWindowForeground(genshinHwnd)
    # 点击账号输入框
    m.click(coordCfg['accountPos'][0], coordCfg['accountPos'][1])
    time.sleep(1)
    selectAll()
    # 输入手机号/邮箱
    kb.type_string(str(account))
    time.sleep(1)
    # 点击密码输入框
    m.click(coordCfg['passwordPos'][0], coordCfg['passwordPos'][1])
    time.sleep(1)
    # 输入密码
    kb.type_string(password)
    time.sleep(1)
    # 点击同意用户协议和隐私政策
    m.click(coordCfg['agreementCheckPos'][0], coordCfg['agreementCheckPos'][1])
    time.sleep(1)
    # 点击进入游戏
    m.click(coordCfg['logInPos'][0], coordCfg['logInPos'][1])
    time.sleep(1)
    # 切换输入法语言为中文
    changeLanguage(genshinHwnd, 'ZH')
    time.sleep(8)
    # 点击登入游戏
    # m.click(coordCfg['logInPos'][0], coordCfg['logInPos'][1])


if __name__ == '__main__':
    main()
