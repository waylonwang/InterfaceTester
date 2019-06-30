# coding=utf-8
import configparser
import os
import time

import ipywidgets as widgets
from IPython.core.display import display
from IPython.core.magic import register_line_magic


def real_path(relative_path):
    base_path = os.path.split(os.path.realpath(__file__))[0]
    return os.path.join(base_path, relative_path)


def clipcopy(value):
    import os
    os.system("echo '%s' | pbcopy" % str(value))



class Debug():
    '''
    调试类
    '''
    enabled = False

    def __init__(self, enabled):
        self.enabled = enabled
        self.widget = widgets.Output()
        self.cleaner = None

    def display(self):
        if self.enabled:
            self.enable()
        else:
            self.disable()
        display(self.widget)

    def enable(self):
        self.enabled = True
        self.widget.layout = widgets.Layout()
        self.cleaner.layout = widgets.Layout()

    def disable(self):
        self.enabled = False
        self.widget.layout = widgets.Layout(display = 'none')
        self.cleaner.layout = widgets.Layout(display = 'none')

    def out(self, info):
        with self.widget:
            print('[%s] %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info))

    def getOutputer(self):
        return self.widget

    def setCleaner(self, wd):
        self.cleaner = wd

    def getCleaner(self):
        return self.cleaner


class Config():
    '''
    配置类
    '''
    cf = configparser.ConfigParser()
    section = None

    def __init__(self, section):
        self.section = section
        self.cf.read(real_path("setting.cfg"))

    def isReady(self):
        '''
        配置项是否已经就绪
        :return: 是否已经就绪
        '''
        if self.section not in self.cf.sections():
            return False
        else:
            return True

    def initConf(self, section):
        '''
        初始化配置项
        :param section: 属性分区
        :return:
        '''
        if section not in self.cf.sections():
            self.cf.add_section(section)

    def writeConf(self, section, name, value):
        '''
        写入配置项
        :param section: 属性分区
        :param name: 属性名称
        :param value: 属性值
        :return:
        '''
        self.cf.set(section, name, value if value is not None else '')
        self.cf.write(open(real_path("setting.cfg"), "w"))

    def readConf(self, section, name, default = None):
        '''
        读取配置项
        :param section: 属性分区
        :param name: 属性名称
        :return: 属性值
        '''
        if name.lower() in self.cf.options(section):
            return self.cf.get(section, name)
        else:
            return default


class Tool():
    '''
    工具类
    '''

    @classmethod
    def generate_nonce(cls, len = 16, lowercase = True, uppercase = False, digits = True):
        '''
        产生nonce
        :param len: 长度
        :param lowercase: 允许小写
        :param uppercase: 允许大写
        :param digits: 允许数字
        :return: nonce
        '''
        import random
        import string
        random.seed()
        chars = ''
        if lowercase: chars += string.ascii_lowercase
        if uppercase: chars += string.ascii_uppercase
        if digits: chars += string.digits
        return ''.join([random.choice(chars) for _ in range(len)])

    @classmethod
    def generate_time(cls):
        '''
        产生时间戳
        :return: 时间戳
        '''
        import time
        return int(time.time() * 1000)

    @classmethod
    def generate_sign(cls, params, secret):
        '''
        产生签名
        :param params: 参数值
        :param secret: 密钥
        :return: 签名
        '''
        params_list = [key + '=' + str(value) + '&' for key, value in params.items() if
                       value is not None or str(value) != '']
        params_list.sort()
        params_str = ''.join(params_list)
        params_str = params_str + 'key=' + secret
        params_str = cls.generate_md5(params_str.encode('utf-8'))
        return params_str

    @classmethod
    def generate_md5(cls, str):
        '''
        产生MD5
        :param str: 二进制字符串
        :return: MD5
        '''
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()