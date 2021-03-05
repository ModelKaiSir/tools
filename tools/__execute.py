import tools
import itertools
import functools
import os
import logging
import fire
import json
import subprocess
import qrcode
from tools import util, encryption
from tools.techtrans import clock, format, replace
from inspect import signature
from tkinter import *
import tkinter.ttk as ttk
from tkinter.filedialog import *
from tkinter.messagebox import *

level_arg = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARRING": logging.WARNING,
    "ERROR": logging.ERROR
}


class ToolsMenu:

    def __init__(self, *args, **kwargs):

        # tools menu 使用自己的log配置
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        #
        log_level = kwargs.get("log") if kwargs.get('log') is not None else "INFO"
        logging.basicConfig(level=level_arg.get(log_level), format='%(asctime)s - %(levelname)s - %(message)s')

        self.logger = logging.getLogger("ToolsMenu")
        if kwargs.get('log_handler'):
            self.logger.addHandler(kwargs.get('log_handler'))
        self.args = args
        self.kwargs = kwargs
        self.logger.debug("args: %s", self.args)
        self.logger.debug("kwargs: %s", self.kwargs)
        pass

    def clock(self):
        """
        科传每日登记
        :param self.kwargs
            name 打卡人姓名
            clock 要登记的源
        """
        if not self.kwargs.get("name"):
            # 默认为我
            self.kwargs.update({"name": "邱凯"})
        if not self.kwargs.get("clock"):
            self.logger.warning("clock: please see %s", clock.URL.keys())
        else:
            self.logger.info("clock to %s", self.kwargs.get("name"))
            clock.clock(**self.kwargs)

    pass

    def format_sql(self):
        """
        格式化sql
        :param self.kwargs
            path 存放sql文件路径
            copy 格式化的文本复制到剪贴板
            override 覆盖到path路径文件中
        """
        path = self.kwargs["path"] if self.kwargs.get("path") else format.DEFAULT_HANDLE_PATH
        self.logger.debug(path)

        if self.kwargs.get("copy"):

            self.logger.debug("copy mode")
            util.copy_text("".join(format.format_sql()))
        elif self.kwargs.get('override'):

            self.logger.debug("override mode")
            _sql = format.format_sql(sql_path=path)
            if _sql is None or len(_sql) < 1:
                self.logger.warning("form sql result is Empty.")
            pass

            for _s in _sql:
                self.logger.debug(_s)
            with open(path, mode="w", encoding="utf-8") as w:
                w.writelines(_sql)
                pass
        else:

            # 默认为copy模式
            self.logger.info("format and copy to CLIPBOARD")
            self.kwargs.update({"copy": 1})
            self.format_sql()
        pass

    def md5(self):

        """
        md5加密
        :param self.args 需要加密的内容，可以是文本或者文件路径
        :param self.kwargs 如果是文件路径 使用File参数 eg d:/t.txt File=1
        结果复制到剪贴板
        """
        if self.kwargs.get('File'):
            self.logger.debug("encryption File md5")
        _r = encryption.md5(*self.args, **self.kwargs)
        for _k, _v in _r.items():
            self.logger.info("%s : %s", _k, _v)

        util.copy_text("-".join([f"{k}:{v}" for k, v in _r.items()]))
        pass

    def replace_class(self):
        """
        生成class替换文件
        :param self.args java文件包名支持多个，支持联想上一个。
        如 org.t.name1 name2 org.t2.name3, name1和name2自动联想为同一包下的两个文件 name3为另外一个包下的文件
        """
        try:
            with open(os.path.join("erp.json"), "r", encoding="utf-8") as j:
                erp_config = json.load(j)

                self.logger.debug("load erp config %s", erp_config)
                assert erp_config is not None, "erp config json is None."

                if self.kwargs.get("root"):
                    self.logger.info("find class path to %s", self.kwargs.get("root"))
                    replace.replace_class(*self.args, **self.kwargs)
                else:
                    _project_path = erp_config["PROJECT_PATH"]
                    _readme = erp_config["README"]
                    self.kwargs.update({"root": _project_path[self.kwargs.get("pos")], "template": _readme})
                    replace.replace_class(*self.args, **self.kwargs)
                pass
        except KeyError:

            self.logger.error("error 相关erp.json配置不存在！")
            pass
        pass

    def qr_code(self):
        """
        生成二维码
        :param self.args 内容
        """

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )

        for _i, _d in enumerate(self.args):
            file_name = f"qrCode{_i}.png" if _i != 0 else "qrCode.png"
            qr.add_data(_d)
            qr.make(fit=True)
            cache_image = qr.make_image()
            cache_image.save(file_name)

            _output = os.path.join(file_name)
            # 显示图片
            subprocess.Popen(_output, shell=True, stdin=subprocess.PIPE, encoding="GBK")
            self.logger.info("save to %s success.", _output)
        pass

    def test(self):

        self.logger.debug("debug test success")
        self.logger.info("info test success")
        self.logger.warning("warning test success")
        self.logger.error("error test success")
        pass


class TextArea(logging.Handler, Text):

    def __init__(self, root, cnf={}, **kwargs):
        logging.Handler.__init__(self, level=kwargs.get('level', logging.NOTSET))
        Text.__init__(self, root, cnf, **kwargs)
        pass

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.configure(state=NORMAL)
        self.insert(END, f"{msg}\n")
        self.configure(state=DISABLED)
        self.see(END)
        pass

    def write(self, s):
        self.configure(state=NORMAL)
        self.insert(END, f"{s}\n")
        self.configure(state=DISABLED)
        self.see(END)

        pass

    pass


def run():
    fire.Fire(ToolsMenu)
    pass


def execute():
    def action_tools(_attr, e):

        _args = args_val.get().split(" ")
        _kwargs = {k: v for k, v in [kw.split("=") for kw in kwargs_val.get().split(" ")]} if bool(
            kwargs_val.get()) else {}

        _kwargs.update({"log_handler": out_put})
        out_put.configure(state=NORMAL)
        out_put.delete(1.0, END)
        tool = ToolsMenu(*_args, **_kwargs)

        sys.stdout = out_put
        help(getattr(tool, _attr))
        if callable(getattr(tool, _attr)):
            getattr(tool, _attr)()

        sys.stdout = sys.__stdout__
        pass

    app = Tk()
    app.title("Tools")

    tools_menu = LabelFrame(app, text="菜单")
    out_put_container = LabelFrame(app, text="结果")
    parameters_container = Frame(out_put_container)

    lb_args = ttk.Label(parameters_container, text="参数1")
    args_val = StringVar()
    entry_args = ttk.Entry(parameters_container, textvariable=args_val)

    kwargs_val = StringVar()
    lb_kwargs = ttk.Label(parameters_container, text="参数2")
    entry_kwargs = ttk.Entry(parameters_container, textvariable=kwargs_val)

    out_put = TextArea(out_put_container)

    for attr in dir(ToolsMenu):

        if not attr.startswith("__") and callable(getattr(ToolsMenu, attr)):
            _b = ttk.Button(tools_menu, text=attr)
            _b.bind("<Button-1>", functools.partial(action_tools, attr))
            _b.pack(side=TOP, padx=2, pady=1)
            pass

        pass

    tools_menu.pack(side=LEFT, fill=BOTH, padx=2, pady=2)

    lb_args.pack(side=LEFT)
    entry_args.pack(side=LEFT)
    lb_kwargs.pack(side=LEFT)
    entry_kwargs.pack(side=LEFT)

    out_put_container.pack(side=TOP, fill=BOTH, expand=YES)
    parameters_container.pack(side=TOP, fill=BOTH)
    out_put.pack(side=TOP, fill=BOTH, pady=3, expand=YES)
    app.mainloop()
    pass


def __test__():
    # ToolsMenu(clock=clock.WJX, name="邱凯").clock()
    # ToolsMenu(copy=1).format_sql()
    # ToolsMenu("com.techtrans.vaadin.espos61.mis.mall.ec.raxh.payment.oline.method.AbstractPayMethod",
    #           "com.techtrans.vaadin.espos61.mis.mall.ec.raxh.payment.oline.OnlinePayFunctionMain",
    #           pos="61").replace_class()
    # ToolsMenu("你说分手").qr_code()
    ToolsMenu(clock="WJX", name="邱凯").clock()


if __name__ == '__main__':
    # __test__()
    t = ToolsMenu("com.techtrans.vaadin.espos61.mis.mall.ec.wzbjgc.report.ContractSettlement_gp", pos="61",
                  suffix='rptdesign')
    execute()
    # getattr(t, "replace_class")()
