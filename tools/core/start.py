import fire
import pathlib
import qrcode
import subprocess

import win32api
import win32con
import win32clipboard as clip
import configparser as parser

from tools.toolKit import encryption, classes, lyric, properties


class Util:

    @staticmethod
    def copy_text(text):
        clip.OpenClipboard()
        clip.EmptyClipboard()
        clip.SetClipboardText(text)
        clip.CloseClipboard()

    @staticmethod
    def copy_file(file):
        clip.OpenClipboard()
        clip.EmptyClipboard()
        clip.SetClipboardData(win32con.CF_DIF, file)
        clip.CloseClipboard()

    @staticmethod
    def get_desktop_path():
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                                  r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders', 0,
                                  win32con.KEY_READ)
        return win32api.RegQueryValueEx(key, 'Desktop')[0]

    pass


pass


class Tools:
    """

    classesTools 可选--suffix参数：查找文件的后缀，默认class
    lrcTools 必填--path参数：需要下载歌词的文件夹（文件）目录
    """

    def __init__(self, **kwargs):

        self.__confIg_path = pathlib.Path().cwd().joinpath("tools.ini")

        if not self.__confIg_path.exists():
            self.__confIg_path.open(mode='a')
            self.__init_classes()
            self.__init_lrc()

        encryption.Util = Util

        _conn = self.__generate_config_parser()
        classes.config = dict(_conn.items('classes'))
        lyric.config = dict(_conn.items('lyricapi'))

        self.classes = classes.ReplaceTool(kwargs.get("suffix"))
        self.encrypted = encryption.EncryptedTool()
        self.lrc = lyric.LrcTools(kwargs.get("path"))
        self.properties = properties.PropertiesManager()
        pass

    def __generate_config_parser(self):

        _conn = parser.ConfigParser()
        _conn.read(self.__confIg_path, encoding='UTF-8')
        return _conn
        pass

    def __init_lrc(self):

        _conn = parser.ConfigParser()
        _conn.read(self.__confIg_path, encoding='UTF-8')
        _section = "lyricapi"
        _conn.add_section(_section)
        _config_parameter = {"api_url": "http://www.douqq.com/qqmusic/qqapi.php",
                             "qq_music_api_url": "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&searchid={timetamp:}&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=10&w={sound:}&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0",
                             "qq_music_comment_cfg_url": "https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=GB2312&notice=0&platform=yqq.json&needNewCode=0&cid={timetamp:}&reqtype=1&biztype=1&topid={id:}&cmd=4&needmusiccrit=0&pagenum=0&pagesize=0&lasthotcommentid=&domain=qq.com",
                             "qq_music_comment_url": "https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=GB2312&notice=0&platform=yqq.json&needNewCode=0&cid={timetamp:}&reqtype=2&biztype=1&topid={id:}&cmd=8&needmusiccrit=0&pagenum={pagenum:}&pagesize={pagesize:}&lasthotcommentid=&domain=qq.com&ct=24&cv=10101010"}

        for k, v in _config_parameter.items():
            _conn.set(_section, k, v)
        _conn.write(open(self.__confIg_path, 'r+'))
        pass

    def __init_classes(self):

        _conn = parser.ConfigParser()
        _conn.read(self.__confIg_path, encoding='UTF-8')
        _section = "classes"
        _conn.add_section(_section)
        _config_parameter = {"generate_zip_path": "C:\\Users\\admin\Desktop\\", "comment": "readMe"}

        for k, v in _config_parameter.items():
            _conn.set(_section, k, v)
        _conn.write(open(self.__confIg_path, 'r+'))

    def config(self, section, **kwargs):

        """ 修改ini配置内容 --section配置名 --参数=参数值 （支持多个）"""
        _conn = parser.ConfigParser()
        _conn.read(self.__confIg_path, encoding='UTF-8')

        if not _conn.has_section(section):
            _conn.add_section(section)
        for k, v in kwargs.items():
            _conn.set(section, k, v)

        _conn.write(open(self.__confIg_path, "r+", encoding='UTF-8'))
        pass

    def qr_code(self, data):
        file_name = "qrCode.png"

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )

        qr.add_data(data)
        qr.make(fit=True)
        cache_image = qr.make_image()
        cache_image.save(file_name)

        # 显示图片
        print(pathlib.Path().cwd().joinpath(file_name))
        subprocess.Popen(str(pathlib.Path().cwd().joinpath(file_name)), shell=True, stdin=subprocess.PIPE,
                         encoding="GBK")

        print("save to " + str(pathlib.Path().cwd().joinpath(file_name)))
        pass

    def __str__(self):
        return 'jobDone'


pass


def main():
    fire.Fire(Tools)
    pass
