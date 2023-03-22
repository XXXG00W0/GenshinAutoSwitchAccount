from pymouse import PyMouse
from pykeyboard import PyKeyboard
import win32api, win32con, win32gui, win32ui
# import win32com.client keyboard, winsound
import ctypes, sys, pandas, json, time, argparse, copy

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


def toDataFrame(cfg):
    header = ['昵称', '账号', '密码']
    # pandas.set_option('display.unicode.anbiguous_as_wide', True) 无法使用
    pandas.set_option('display.unicode.east_asian_width', True)
    pandas.set_option('display.width', 180)
    pswdList = list([k, v[0], v[1]] for k, v in cfg['account'].items())
    pswdDataFrame = pandas.DataFrame(pswdList, columns=header)
    return pswdDataFrame


def printDataFrame(df, hide_password=True):
    if len(df.index) == 0:
        print('表格为空')
        return
    tempdf = copy.deepcopy(df)
    hiddenPswd = pandas.DataFrame([['********'] for i in range(len(tempdf.index))])
    tempdf['密码'] = hiddenPswd
    print(tempdf)

def addAccount(cfg, args):
    continueAdd = True
    pswdDataFrame = toDataFrame(cfg)
    # 储存了密码 且 用户需要添加密码 才打印
    if len(pswdDataFrame) != 0 and args.add_account:
        printDataFrame(pswdDataFrame, args.hide_password)
    # 储存了密码 且 用户不需要添加密码 则返回，不添加账户
    if not args.add_account and len(pswdDataFrame) != 0:
        return cfg

    # 如果添加账户 或 账户为空 或 还继续添加 则用户此次启动会添加密码
    while continueAdd:

        # 用户还没有密码
        if len(pswdDataFrame) == 0:
            print(f'当前账密信息为空，现在添加账密')

        altName = input('请输入昵称：')
        account = input('请输入账号：')
        pswd = input('请输入密码：')
        pswdDataFrame.loc[len(pswdDataFrame.index)] = [altName, account, pswd]
        cfg['account'][altName] = [account, pswd]
        printDataFrame(pswdDataFrame, args.hide_password)

        # 询问是否继续添加密码
        if input('已添加，是否继续（是Y/否N）').lower() == 'n':
            continueAdd = False

    return cfg

def main(args, cfg):

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

    # 从cfg字典中读取账密
    cfg = addAccount(cfg, args)

    # 询问账号索引，若索引错误则重新询问
    pswdDataFrame = toDataFrame(cfg)
    printDataFrame(pswdDataFrame, args.hide_password)
    while 1:
        try:
            accountIndex = input('输入需要切换的账号序号：')
            accountIndex = int(accountIndex)
            row = pswdDataFrame.iloc[accountIndex]  # iloc 位置索引，loc 标签索引
            account = row.loc['账号']
            password = row.loc['密码']
            print("选定账户：\n", row.to_string())
        except ValueError:
            print(f'"{accountIndex}"不是有效序号')
        except (KeyError, IndexError):
            print(f'输入的序号"{accountIndex}"不存在')
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
    m.click(coordCfg['logInPos'][0], coordCfg['logInPos'][1])


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--add-account', action='store_true', help='若有该参数，则添加账密后再输入密码')
    parser.add_argument('-p', '--hide-password', action='store_true', help='若有该参数，则不显示密码')
    args = parser.parse_args()

    # 查询是否以管理员权限启动（原作者：https://blog.csdn.net/MemoryD/article/details/83148305）
    if not isAdmin():
        print("未使用管理员权限运行，将无法填写账密")

        # 请求管理员权限
        # https://blog.csdn.net/weixin_42413844/article/details/120064752
        # sys.version_info 是一个包含了版本号5个组成部分的元祖，
        # 这5个部分分别是主要版本号（major）、次要版本号（minor）、微型版本号（micro）、发布级别（releaselevel）和序列号（serial）
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print("已使用管理员权限运行")
    cfg = readConfig('./config.json')
    if not cfg:
        exit(1)
    main(args, cfg)
