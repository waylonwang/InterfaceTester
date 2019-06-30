# coding=utf-8
import pandas as pd
import qgrid
from IPython.core.display import display
from colorama import Fore
from ipywidgets.widgets import Layout, Label, Button, Dropdown, ToggleButton, DatePicker, IntText, Text, Textarea, HTML,\
    Box, VBox, Accordion

from api import servers, interfaces
from tester import testers
from util import Debug, Config, Tool



GLOBAL_SECTION = 'global'
debug = Debug(False)
ref = []


class Interface():
    '''
    接口类
    '''

    def __init__(self, default):
        self.default = default # 默认配置{catagory,interface}
        self.cf = Config(self.default['interface']) # 配置对象

    def __repr__(self):
        return '[Interface Object: catagoryname = %s , interfacename = %s]' % (self.catagoryname, self.interfacename)

    def on_catagory_change(self, change):
        '''
        更改类别
        :param change: 更改内容
        :return: 
        '''
        if change['type'] == 'change' and change['name'] == 'value':
            debug.out('on_catagory_change event')
            self.catagoryname = change['new']
            self.interfacename = None # 清空接口名称
            self.catagory = interfaces.get(self.catagoryname, None) if self.catagoryname is not None else None # 类别信息
            self.interfaces = self.catagory.get('interface', None) if self.catagory is not None else None # 类别下所有接口信息
            self.interface = None # 清空接口信息
            # 写入配置项
            debug.out('on_catagory_change before write conf\ncatagoryname=%s\ninterfacename=%s' % (
                self.catagoryname, self.interfacename))
            self.cf.writeConf(self.default['interface'], 'catagoryname', self.catagoryname)
            self.cf.writeConf(self.default['interface'], 'interfacename', self.interfacename)
            # 修改界面
            debug.out('on_catagory_change before modify UI')
            self.htmInterface.value = self.choiceResult()
            self.dpInterface.options = [key for key in self.interfaces.keys()]

    def on_interface_change(self, change):
        '''
        更改接口
        :param change: 更改内容
        :return: 
        '''
        if change['type'] == 'change' and change['name'] == 'value':
            debug.out('on_interface_change event')
            self.interfacename = change['new']
            self.interfaces = self.catagory.get('interface', None) if self.catagory is not None else None # 类别下所有接口信息
            self.interface = self.interfaces.get(self.interfacename,
                                                 None) if self.interfaces is not None and self.interfacename is not None else None # 接口信息
            # 写入配置项
            debug.out('on_interface_change before write conf\ninterfacename=%s' % self.interfacename)
            self.cf.writeConf(self.default['interface'], 'interfacename', self.interfacename)
            # 修改界面
            debug.out('on_interface_change before modify UI')
            self.htmInterface.value = self.choiceResult()
            self.dfParams = pd.DataFrame(self.interface['params'], index = [0]).T
            self.dfParams.columns = ['请求参数类型']
            self.gdParam.df = self.dfParams

            self.dfBody = pd.DataFrame(self.interface.get('body', ['无']))
            self.dfBody.columns = ['请求体参数名称']
            self.gdBody.df = self.dfBody

            self.packageWidgets()
            self.packageParams()

    def on_init_clicked(self, b):
        '''
        点击初始化按钮
        :param b: 按钮
        :return: 
        '''
        debug.out('on_init_clicked event')
        self.cf.initConf(self.default['interface'])
        self.cf.writeConf(self.default['interface'], 'catagoryname', self.default['catagory'])
        self.cf.writeConf(self.default['interface'], 'interfacename', self.default['interface'])

    def on_param_change(self, change):
        '''
        参数输入变化
        :param change: 新的参数值
        :return: 
        '''
        if change['type'] == 'change' and change['name'] == 'value':
            self.packageParams()

    def on_execute_clicked(self, b):
        '''
        点击执行请求按钮
        :param b: 按钮
        :return: 
        '''
        debug.out('on_execute_clicked event')
        import requests
        if self.interface['method'] == 'GET':
            self.r = requests.get('http://' + self.env.server + self.interface['url'], params = self.params)
            self.htmExecute.value = '<span style="color:#208FFB">[%s请求执行完成] --> %s</span>' % (
                self.interface['method'], self.r.url)
        elif self.interface['method'] == 'POST':
            if self.interface.get('body', False) != False:
                self.r = requests.post('http://' + self.env.server + self.interface['url'], params = self.params,
                                       data = self.data)
            else:
                self.r = requests.post('http://' + self.env.server + self.interface['url'], params = self.params)
            self.htmExecute.value = '<span style="color:#208FFB">[%s请求执行完成] --> %s</span>' % (
                self.interface['method'], self.r.url)
        else:
            self.htmExecute.value = '<span style="color:red">[%s接口方法填写错误，请求未执行]</span>' % self.interface['method']

        if self.gdResult is not None:
            import json
            output = json.loads(self.r.text)
            resultCode = output['resultCode']
            debug.out('resultCode = %s' % resultCode)
            if resultCode == 1:
                debug.out('response output: %s' % output)
                self.htmResult.value = '<span style="color:#208FFB">[请求成功] 返回数据：</span>'
                for field in self.interface['output']:
                    output = output[field]
                df = pd.DataFrame(output)
                self.gdResult.df = df
                self.gdResult.layout = Layout()
            else:
                self.htmResult.value = output['<span style="color:red">请求失败：%s</span>' % output['resultMsg']]
                self.gdResult.layout = Layout(display = 'none')

    def on_copy_clicked(self, b):
        # pyperclip.copy(self.r.url)
        pass

    def choiceResult(self):
        '''
        获取环境选择结果
        :return: 选择结果
        '''
        try:
            return '<span style="color:#208FFB">当前选择的接口是: [%s]<br>url = %s<br>method = %s<br>output = %s </span>' % (
                self.interface.get('desc', ''), self.interface.get('url', ''), self.interface.get('method', ''),
                self.interface.get('output', ''))
        except:
            return ''

    def packageWidgets(self):
        '''
        打包组件
        :return: 
        '''
        debug.out('package request widgets')
        self.paramWidgets = {}
        self.txtBody = None
        for param, ptype in self.interface['params'].items():
            value = self.cf.readConf(self.default['interface'], param)
            if ptype == 'int':
                pw = IntText(description = param + ':',
                             value = value if value is not None else 0,
                             layout = Layout(width = '90%'))
            elif ptype == 'date':
                pw = DatePicker(description = param + ':',
                                value = value if value is not None else '',
                                layout = Layout(width = '90%'))
            elif ptype == 'companyId':
                pw = Text(description = param + ':',
                          value = value if value is not None else self.env.tester['companyId'],
                          layout = Layout(width = '90%'))
            elif ptype == 'openId':
                pw = Text(description = param + ':',
                          value = value if value is not None else self.env.tester['openId'],
                          layout = Layout(width = '90%'))
            else:
                pw = Text(description = param + ':',
                          value = value if value is not None else '',
                          layout = Layout(width = '90%'))
            pw.observe(self.on_param_change)
            self.paramWidgets[param] = pw

        self.txtBody = Textarea(description = 'body data:', value = '')
        self.txtBody.layout = Layout(display = 'none')

        debug.out(self.interface.get('body', False))
        if self.interface.get('body', False) != False:
            debug.out('interface have body data to package widget')
            value = self.cf.readConf(self.default['interface'], 'body')
            self.txtBody.value = value if value is not None else ''
            self.txtBody.layout = Layout(width = '90%', height = '200px')

        tmpWds = [wd for wd in self.paramWidgets.values()]
        tmpWds.append(self.txtBody)
        self.boxParams.children = tmpWds

    def packageParams(self):
        '''
        打包数据
        :return: 
        '''
        debug.out('package request params')
        self.params = {}
        for param, widget in self.paramWidgets.items():
            self.params[param] = str(widget.value)
            self.cf.writeConf(self.env.default['interface'], param, str(widget.value))
        self.params['appKey'] = self.env.tester['api_key'][self.catagoryname]
        self.params['nonce'] = Tool.generate_nonce()
        self.params['time'] = Tool.generate_time()
        self.params['sign'] = Tool.generate_sign(self.params, self.env.tester['api_secret'][self.catagoryname])

        df = pd.DataFrame(self.params, index = [0]).T
        df.columns = ['参数值']
        self.gdParamValue.df = df

        debug.out(self.interface.get('body', False))
        if self.interface.get('body', False) != False:
            debug.out('interface have body data to package params')
            self.data = self.txtBody.value
            self.cf.writeConf(self.env.default['interface'], 'body', self.txtBody.value)

        else:
            self.data = None
            self.cf.writeConf(self.env.default['interface'], 'body', '')

    def displayInterface(self):
        '''
        显示组件
        :return: 
        '''
        if not self.cf.isReady():
            print(Fore.RED + '配置项尚未初始化!')
            self.btnInit = Button(description = '立即初始化', button_style = 'danger')
            self.btnInit.on_click(self.on_init_clicked)
            display(self.btnInit)
        else:
            self.catagoryname = self.cf.readConf(self.default['interface'], 'catagoryname') # 类别名称
            self.catagoryname = self.default[
                'catagory'] if self.catagoryname is None else self.catagoryname # 未设置时使用默认配置
            self.interfacename = self.cf.readConf(self.default['interface'], 'interfacename') # 接口名称
            self.interfacename = self.default[
                'interface'] if self.interfacename is None else self.interfacename # 未设置时使用默认配置
            self.catagory = interfaces.get(self.catagoryname, None) if self.catagoryname is not None else None # 类别信息
            self.interfaces = self.catagory.get('interface', None) if self.catagory is not None else None # 类别下所有接口信息
            self.interface = self.interfaces.get(self.interfacename,
                                                 None) if self.interfaces is not None and self.interfacename is not None else None # 接口信息
            # 组件初始化
            self.dpCatagory = Dropdown(
                options = [key for key in interfaces.keys()],
                value = self.catagoryname if self.catagoryname is not None else None,
                description = '类别:'
            )
            debug.out('interfacename = %s' % self.interfacename)
            tmpOptions = [key for key in
                          interfaces[self.dpCatagory.value]['interface']] if self.catagory is not None else []
            self.dpInterface = Dropdown(
                options = tmpOptions,
                value = self.interfacename if self.interfacename in tmpOptions else None,
                description = '接口:'
            )

            self.dpCatagory.observe(self.on_catagory_change)
            self.dpInterface.observe(self.on_interface_change)

            self.htmInterface = HTML(value = self.choiceResult())
            self.gdParam = qgrid.show_grid(pd.DataFrame(None))
            self.gdBody = qgrid.show_grid(pd.DataFrame(None))

            if self.interface is not None:
                self.dfParams = pd.DataFrame(self.interface.get('params', ['无']), index = [0]).T
                self.dfParams.columns = ['请求参数类型']
                self.gdParam = qgrid.show_grid(self.dfParams,
                                               grid_options = {'filterable': False, 'editable': False})
                self.gdParam.layout = Layout(width = '90%')

                self.dfBody = pd.DataFrame(self.interface.get('body', ['无']))
                self.dfBody.columns = ['请求体参数名称']
                self.gdBody = qgrid.show_grid(self.dfBody, grid_options = {'filterable': False, 'editable': False})
                self.gdBody.layout = Layout(width = '90%')

            debug.out('display from interface object=%s' % self)
            display(self.dpCatagory)
            display(self.dpInterface)

            boxRequest = Box([VBox([Label(value = '请求参数:'), self.gdParam],
                                   layout = Layout(flex = '1 1 0%', width = 'auto')),
                              VBox([Label(value = '请求体参数:'), self.gdBody],
                                   layout = Layout(flex = '1 1 0%', width = 'auto'))],
                             layout = Layout(flex_flow = 'row', display = 'flex'))
            boxRef = VBox([self.htmInterface, boxRequest])
            acRef = Accordion(children = [boxRef])
            acRef.set_title(0, '接口参考')
            toggleRefDisplay(acRef)
            display(acRef)
            ref.append(acRef)

    def displayPrepare(self, env):
        '''
        准备数据
        :param env: 当前环境
        :return: 
        '''
        self.env = env
        if not self.cf.isReady():
            print(Fore.RED + '配置项尚未初始化!')
        else:
            self.boxParams = VBox()
            self.boxParams.layout = Layout(flex_flow = 'column', display = 'flex')
            self.packageWidgets()
            display(self.boxParams)

            self.gdParamValue = qgrid.show_grid(pd.DataFrame([]),
                                                grid_options = {'filterable': False, 'autoHeight': True,
                                                                'editable': False})
            self.gdParamValue.layout = Layout(width = '90%')
            self.packageParams()
            self.txtBodyValue = Textarea(value = self.data if self.data is not None else '')
            self.txtBodyValue.layout = Layout(width = '90%', height = '200px', margin = '6px 2px 2px 2px')

            boxRequest = Box([
                VBox([Label(value = '请求参数值:'), self.gdParamValue],
                     layout = Layout(flex = '1 1 0%', width = 'auto')),
                VBox([Label(value = '请求体参数值:'), self.txtBodyValue],
                     layout = Layout(flex = '1 1 0%', width = 'auto'))],
                layout = Layout(flex_flow = 'row', display = 'flex'))
            acRef = Accordion(children = [boxRequest])
            acRef.set_title(0, '输入参考')
            toggleRefDisplay(acRef)
            display(acRef)
            ref.append(acRef)

    def displayExecute(self):
        '''
        执行请求
        :return: 
        '''
        if not self.cf.isReady():
            print(Fore.RED + '配置项尚未初始化!')
        elif self.env.tester is not None:
            self.btnExecute = Button(description = '执行请求', button_style = 'primary')
            btnCopy = Button(description = '复制请求链接')

            self.btnExecute.on_click(self.on_execute_clicked)
            btnCopy.on_click(self.on_copy_clicked)

            self.htmExecute = HTML(value = '')
            # boxExecute = VBox([Box([self.btnExecute, btnCopy]), self.htmExecute])
            boxExecute = VBox([self.btnExecute, self.htmExecute])

            display(boxExecute)

    def displayResponse(self):
        '''
        查看结果
        :return: 
        '''
        if not self.cf.isReady():
            print(Fore.RED + '配置项尚未初始化!')
        else:
            self.htmResult = HTML(value = '')
            self.gdResult = qgrid.show_grid(pd.DataFrame([]))
            boxResult = VBox([self.htmResult, self.gdResult])
            display(boxResult)


class Env():
    '''
    环境类
    '''

    cf = None

    def __init__(self, default):
        self.default = default # 默认配置{catagory,interface}
        self.cf = Config(self.default['interface']) # 配置对象

    def __repr__(self):
        return '[Env Object: envcode = %s , testercode = %s]' % (self.envcode, self.testercode)

    def on_env_change(self, change):
        '''
        更改环境
        :param change: 更改内容
        :return: 
        '''
        if change['type'] == 'change' and change['name'] == 'value':
            debug.out('on_env_change event')
            self.envcode = change['new']
            self.testercode = None # 清空测试员代码
            self.server = servers[self.envcode] if self.envcode is not None else None
            self.tester = None # 清空测试信息

            # 写入配置项
            debug.out('on_env_change before write conf\nenvcode=%s\ntestercodee=%s' % (
                self.envcode, self.testercode))
            self.cf.writeConf(self.default['interface'], 'env', self.envcode)
            self.cf.writeConf(self.default['interface'], 'tester', self.testercode)

            # 修改界面
            debug.out('on_env_change before modify UI')
            self.htmEnv.value = self.choiceResult()
            self.dpTester.options = [key for key, value in testers.items() if value['envcode'] == self.dpEnv.value]

    def on_tester_change(self, change):
        '''
        更改测试员
        :param change: 更改内容
        :return: 
        '''
        if change['type'] == 'change' and change['name'] == 'value':
            debug.out('on_tester_change event')
            self.testercode = change['new']
            self.tester = testers[self.testercode] if self.testercode is not None else None

            # 写入配置项
            debug.out('on_tester_change before write conf\ntestercode=%s' % self.testercode)
            self.cf.writeConf(self.default['interface'], 'tester', self.testercode)

            # 修改界面
            debug.out('on_tester_change before modify UI')
            self.htmEnv.value = self.choiceResult()

    def choiceResult(self):
        '''
        获取环境选择结果
        :return: 选择结果 
        '''
        try:
            return '<span style="color:#208FFB">当前选择的环境是: %s --> %s<br>当前选择的账号是: %s<br>'\
                   'api_key = %s<br>api_secret = %s</span>' % (
                       self.envcode if self.envcode is not None else '',
                       self.server if self.server is not None else '',
                       self.testercode if self.testercode is not None else '',
                       testers[self.testercode]['api_key'][self.catagoryname] if self.testercode is not None else '',
                       testers[self.testercode]['api_secret'][self.catagoryname] if self.testercode is not None else '')
        except:
            return ''

    def displayEnv(self):
        '''
        显示环境组件
        :return: 
        '''
        if not self.cf.isReady():
            print(Fore.RED + '配置项尚未初始化!')
        else:
            self.envcode = self.cf.readConf(self.default['interface'], 'env') # 环境代码
            self.testercode = self.cf.readConf(self.default['interface'], 'tester') # 测试员代码
            self.catagoryname = self.cf.readConf(self.default['interface'], 'catagoryname') # 接口类别名称
            self.server = servers[self.envcode] if self.envcode is not None else None # 服务器地址
            self.tester = testers[self.testercode] if self.envcode is not None else None # 测试信息
            # 组件初始化
            self.dpEnv = Dropdown(
                options = [key for key, value in servers.items()],
                value = self.envcode if self.envcode is not None else None,
                description = '环境:'
            )
            self.dpTester = Dropdown(
                options = [key for key, value in testers.items() if value['envcode'] == self.dpEnv.value],
                value = self.testercode if self.testercode is not None else None,
                description = '账号:'
            )

            self.dpEnv.observe(self.on_env_change)
            self.dpTester.observe(self.on_tester_change)

            self.htmEnv = HTML(value = self.choiceResult())

            debug.out('display from env object=%s' % self)
            display(self.dpEnv)
            display(self.dpTester)

            acRef = Accordion(children = [self.htmEnv])
            acRef.set_title(0, '环境参考')
            toggleRefDisplay(acRef)
            display(acRef)
            ref.append(acRef)


def on_ref_change(change):
    '''
    更改参考显示
    :param change: 新的参考状态
    :return: 
    '''
    if change['type'] == 'change' and change['name'] == 'value':
        debug.out(change['owner'])
        config = Config(GLOBAL_SECTION)
        if not config.isReady():
            config.initConf(GLOBAL_SECTION)
        config.writeConf(GLOBAL_SECTION, 'ref', str(change['new']))
        if change['new']:
            change['owner'].description = '隐藏参考信息'
        else:
            change['owner'].description = '显示参考信息'
        for wd in ref:
            toggleRefDisplay(wd)


def on_debug_change(change):
    '''
    更改调试显示
    :param change: 新的显示状态
    :return: 
    '''
    if change['type'] == 'change' and change['name'] == 'value':
        debug.out(change['owner'])
        config = Config(GLOBAL_SECTION)
        if not config.isReady():
            config.initConf(GLOBAL_SECTION)
        config.writeConf(GLOBAL_SECTION, 'debug', str(change['new']))
        if change['new']:
            debug.enable()
            change['owner'].description = '隐藏调试信息'
        else:
            debug.disable()
            change['owner'].description = '显示调试信息'


def on_debugclear_clicked(b):
    '''
    点击调试清除
    :param b: 按钮
    :return: 
    '''
    debug.getOutputer().clear_output()


def toggleRefDisplay(wd):
    '''
    切换参考区域
    :param wd: 参考区域
    :return: 
    '''
    config = Config(GLOBAL_SECTION)
    if config.readConf(GLOBAL_SECTION, 'ref', 'True') == str(True):
        wd.layout = Layout()
    else:
        wd.layout = Layout(display = 'none')


def displayGlobalButton():
    '''
    显示全局按钮
    :return: 
    '''
    config = Config(GLOBAL_SECTION)
    if not config.isReady():
        config.initConf(GLOBAL_SECTION)
        config.writeConf(GLOBAL_SECTION, 'ref', 'True')
        config.writeConf(GLOBAL_SECTION, 'debug', 'False')

    isDisplayRef = config.readConf(GLOBAL_SECTION, 'ref', 'True') == str(True)
    isDisplayDebug = config.readConf(GLOBAL_SECTION, 'debug', 'True') == str(True)

    btnRef = ToggleButton(description = '隐藏参考信息' if isDisplayRef else '显示参考信息', value = isDisplayRef)
    btnDebug = ToggleButton(description = '隐藏调试信息' if isDisplayDebug else '显示调试信息', value = isDisplayDebug)
    btnDebugClear = Button(description = '清除调试信息')

    debug.setCleaner(btnDebugClear)

    if isDisplayDebug:
        debug.enable()
    else:
        debug.disable()

    btnRef.observe(on_ref_change)
    btnDebug.observe(on_debug_change)
    btnDebugClear.on_click(on_debugclear_clicked)

    boxGlobal = Box([btnRef, btnDebug, btnDebugClear])
    display(boxGlobal)