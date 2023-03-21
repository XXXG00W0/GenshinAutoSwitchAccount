# GenshinAutoSwitchAccount

基于Python的自动切换原神账号脚本（自己平时帮朋友养号时候用的）<br>
脚本运行的时候，可以去喝口水、上个厕所、或者刷手机，总之不需要自己输密码 <br>
<i>目前仅支持16比9（1920\*1080、2560\*1440，3840\*2160等等）独占全屏</i> <br>
<b>注意：密码均为明文储存，请勿将本地的项目文件（尤其是csv文件）分享给陌生人，以免泄露账密信息</b><br>

## 部署教程

1. 安装 Python (>=3.8)<br>
2. 运行 ```pip install requirements.txt```<br>
3. 首次启动前需要向config.json添加账密，以格式```"account":"password"```添加<br>
4. 双击```Switch Account.bat```即可启动脚本

## 可能遇到的问题

### ```ModuleNotFoundError: No module named 'windows'```
如果遇到这样的错误信息：
```  
File "X:\<Python安装路径>\lib\site-packages\pymouse\__init__.py", line 92, in <module>
    from windows import PyMouse, PyMouseEvent
ModuleNotFoundError: No module named 'windows'
```
我在网上找到的[解决方法](https://cloud.tencent.com/developer/article/1682994)是：<br>
 - 找到```<Python安装路径>\lib\site-packages\pymouse\__init__.py```<br>
 - 然后用任意编辑器打开，找到第92行或```from windows import PyMouse, PyMouseEvent```<br>
 - 将其改成```from pymouse.windows import PyMouse, PyMouseEvent```

### ```ModuleNotFoundError: No module named 'pyhook'```
可能这个的问题会在解决上面的问题后出现，错误信息如下：
```
File "X:\<Python安装路径>\lib\site-packages\pymouse\windows.py", line 23, in <module>
    import pythoncom, pyhook
ModuleNotFoundError: No module named 'pyhook'
```
直接用```pip install pyhook```在我这并不是很好用<br>
所以可以使用PyHook3替换pyhook，安装方法请看[PyHook3 的下载与安装](https://blog.csdn.net/weixin_45752790/article/details/112503807)
