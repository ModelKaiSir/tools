import sqlite3
import logging
from typing import Dict, Any

from tools.techtrans import format
from tools import properties, util
from tkinter import *
import tkinter.ttk as ttk
from tkinter.filedialog import *
from tkinter.messagebox import *

"""一系列带界面的小工具"""
"""科传项目管理工具"""


class _MallPosBean:

    def __init__(self, _id):
        self._id = _id
        self._name = None
        self._type = None
        self._url = None
        self._properties_path = None
        self._properties = None  # type:properties.Properties
        pass

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, _name):
        self._name = _name
        pass

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, _type):
        self._type = _type
        pass

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, _url):
        self._url = _url
        pass

    @property
    def properties_path(self):
        return self._properties_path

    @properties_path.setter
    def properties_path(self, _path):
        self._properties_path = _path

    @property
    def properties(self):
        return self._properties
        pass

    @properties.setter
    def properties(self, _properties):
        self._properties = _properties

    def to_values(self):
        return self._id, self._name, self._type, self._url

    pass


class _MallPosDao:

    def __init__(self):
        # 初始化数据库
        self.conn = sqlite3.connect("mall_pos.db")
        sql_list = format.format_sql("mall_pos.sql")

        for sql in sql_list:
            try:
                self.conn.execute(sql)
            except sqlite3.OperationalError as er:

                logger.info(er)
                pass

        self.conn.commit()
        self.UPDATE = "update pos set name=?, db_type=? url=?, path =? where id= ?"
        self.DELETE = "delete from pos where id =?"
        self.DELETE_ALL = "delete from pos"
        pass

    def add(self, _bean: _MallPosBean):
        _update = "insert into pos (name, db_type, url, path) values (?, ?, ?, ?)"
        self.conn.execute(_update, (_bean.name, _bean.type, _bean.url, _bean.properties_path,))
        _select = "select max(id) from pos"
        self.conn.commit()

        _id = self.conn.execute(_select).fetchall()[0][0]
        _nb = _MallPosBean(_id)
        _nb.name = _bean.name
        _nb.type = _bean.type
        _nb.url = _bean.url
        _nb.properties_path = _bean.properties_path
        _nb.properties = _bean.properties

        if _nb.properties is not None:
            _update = "insert into POS_PROPERTIES (id, pid, PROPERTIES) values (?, ?, ?)"
            for _pid, _properties_item in enumerate(_nb.properties.items()):
                self.conn.execute(_update, (_nb.id, _pid, _properties_item,))
            self.conn.commit()
        del _bean
        return _nb
        pass

    def update(self, _bean: _MallPosBean):

        _update = "insert or replace into pos (id, name, db_type, url, path) values (?, ?, ?, ?, ?)"
        self.conn.execute(_update, (_bean.id, _bean.name, _bean.type, _bean.url, _bean.properties_path,))
        _clear = "delete from pos_properties where id = ?"
        self.conn.execute(_clear, (_bean.id,))
        _update = "insert or replace into POS_PROPERTIES (id, pid, PROPERTIES) values (?, ?, ?)"
        for _pid, _properties_item in enumerate(_bean.properties.items()):
            self.conn.execute(_update, (_bean.id, _pid, _properties_item,))
        self.conn.commit()
        pass

    def _get_bean(self, _r) -> _MallPosBean:

        _id = _r[0]
        bean = _MallPosBean(_id)
        bean.name = _r[1]
        bean.type = _r[2]
        bean.url = _r[3]
        bean.properties_path = _r[4]

        if bean.properties_path is None:
            return bean
        # load properties
        _query = "SELECT PROPERTIES FROM POS_PROPERTIES WHERE ID = ?"
        _result = self.conn.execute(_query, (_id,))
        __result = _result.fetchall()

        if __result is None or len(__result) < 1:
            # load for file
            bean.properties = properties.load(bean.properties_path)
        else:
            # load for data
            bean.properties = properties.loads(bean.properties_path, [str(_v[0]) for _v in __result])
        return bean
        pass

    def get(self, _id) -> _MallPosBean:
        _query = "SELECT ID, NAME, DB_TYPE, URL, PATH FROM POS  where id = ?"
        _result = self.conn.execute(_query, (_id,))
        _bean = None

        for _r in _result:
            _bean = self._get_bean(_r)
            pass

        return _bean
        pass

    def get_all(self):

        _query = "SELECT ID, NAME, DB_TYPE, URL, PATH FROM POS"
        _result = self.conn.execute(_query)
        _result_data = []  # type:list[_MallPosBean]

        for _r in _result:
            _result_data.append(self._get_bean(_r))
            pass

        return _result_data
        pass

    def delete(self, _id):

        _delete = "delete from pos where id = ?"
        self.conn.execute(_delete, (_id,))
        _delete = "delete from pos_properties where id = ?"
        self.conn.execute(_delete, (_id,))
        self.conn.commit()
        pass

    def delete_all(self):

        _delete = "delete from pos"
        self.conn.execute(_delete)
        _delete = "delete from pos_properties"
        self.conn.execute(_delete)
        self.conn.commit()
        pass


class _MallPosUI:
    table: ttk.Treeview

    def __init__(self):

        self.dao = _MallPosDao()
        self.root = Tk()
        self.root.title("MallPosManager")
        self.table = None
        self.header = ("ID", "名称", "数据库类型", "项目地址")
        self.menu_bar()
        self.toolbar()
        self.pos_table()
        center(self.root)
        self.root.mainloop()
        pass

    def pos_table(self):
        table_container = LabelFrame(self.root, text="pos列表")
        self.table = ttk.Treeview(table_container, show="headings", column=self.header)
        for _id, _c in enumerate(self.header):
            self.table.heading(_id, text=_c)
            self.table.column(_id, anchor=S)
            pass
        # _tree.insert('', END, values=("世贸商城", "Oracle", "localhost:8080"))
        self.refresh_data()
        self.table.bind("<Double-Button-1>", self.update)
        self.table.pack(side=LEFT, fill=X, padx=2, pady=5)
        table_container.pack(side=LEFT)
        pass

    def refresh_data(self, event=None):

        logger.debug("refresh data")
        # 清空
        [self.table.delete(_item) for _item in self.table.get_children()]
        # insert data
        for _item in self.dao.get_all():
            self.table.insert('', END, values=_item.to_values())
            pass
        pass

    def menu_bar(self):
        bar = Menu(self.root, tearoff=0)
        menu = Menu(bar)
        menu.add_command(label="New", command=self.add)
        menu.add_command(label="Quit", command=self.save_exit)
        bar.add_cascade(label="Option", menu=menu)
        self.root.config(menu=bar)
        pass

    def toolbar(self):
        container = Frame(self.root)
        copy = ttk.Button(container, text="克隆", command=self.clone)
        delete = ttk.Button(container, text="删除", command=self.delete)
        copy.pack(side=LEFT, padx=2)
        delete.pack(side=LEFT, padx=2)
        container.pack(side=TOP, fill=X, pady=5)

        pass

    def delete(self):

        _select_item = self.table.selection()
        try:
            assert _select_item is not None
            assert len(_select_item) > 0, "请选择要删除的行!"

            multi = len(_select_item) > 1
            for _si in _select_item:
                _values = self.table.item(_si, option="values")
                self.dao.delete(_values[0])
                pass

            if not multi:
                showinfo("提示", f"删除{_values[1]}成功！")
            else:
                showinfo("提示", f"删除成功！")
            pass

            self.refresh_data()
        except AssertionError as e:

            logger.error(e)
            showerror("错误！", e)
            pass
        pass

    def _update(self, event=None, save_update=None, values=None):
        def save():
            nonlocal _bean
            _bean.name = data_form.name
            _bean.type = data_form.type
            _bean.url = data_form.url
            _bean.properties_path = _pf.path
            _bean.properties = _pf.properties
            save_update(_bean)
            pass

        def switch():
            nonlocal _bean
            _bean.properties.finish()
            showinfo("提示", f"成功切换到项目{_bean.name}！")

        def run_pos():
            nonlocal _bean
            connection_url = _bean.properties.get("DatabaseConnectionUrl")
            db_user = _bean.properties.get("DatabaseUser")
            db_password = _bean.properties.get("DatabasePassword")
            auto_login(connection_url, db_user, db_password, _bean.url)

        _bean = self.dao.get(values[0])
        update = Toplevel(self.root)
        update.title("修改项目")

        data_form = _MallPosForm(update, text="项目参数")
        data_form.set_data(_bean)
        _pf = _PropertiesForm(update, text="config.properties")
        _pf.set_config(_bean.properties_path, _bean.properties)
        save = ttk.Button(update, text="保存", command=save)

        option_bar = Frame(update)

        switch = ttk.Button(option_bar, text="切换到此项目", command=switch)
        run = ttk.Button(option_bar, text="启动项目", command=run_pos)

        data_form.pack(fill=X)
        _pf.pack(side=TOP, fill=X)
        switch.pack(side=LEFT)
        run.pack(side=LEFT)
        option_bar.pack(side=BOTTOM)

        save.pack(side=BOTTOM, fill=X)

        update.bind("<Destroy>", self.refresh_data)
        center(update)
        # 置于最上层
        update.transient(self.root)
        update.mainloop()
        pass

    def update(self, event=None):

        def update(_bean):
            nonlocal self
            self.dao.update(_bean)
            showinfo("提示", "保存成功！")
            pass

        try:
            _select_item = self.table.selection()
            assert _select_item is not None
            assert len(_select_item) > 0, "没有选择的项目！"
            _values = self.table.item(_select_item[0], option="values")
            self._update(save_update=update, values=_values)
        except AssertionError as e:
            logger.error(e)
            showerror("错误！", e)
            pass
        pass

    def clone(self):

        def add(_bean):
            nonlocal self
            self.dao.add(_bean)
            nonlocal old_name
            showinfo("提示", f"克隆{old_name}成功！")
            pass

        try:
            _select_item = self.table.selection()
            assert _select_item is not None, "请选择要克隆的项目！"
            assert len(_select_item) > 0, "请选择要克隆的项目！"
            _values = self.table.item(_select_item[0], option="values")
            old_name = _values[1]
            self._update(save_update=add, values=_values)
        except AssertionError as e:
            logger.error(e)
            showerror("错误！", e)
            pass
        pass

    def add(self):
        def save():
            nonlocal new_bean
            new_bean.name = data_form.name
            new_bean.type = data_form.type
            new_bean.url = data_form.url
            new_bean.properties_path = _pf.path
            new_bean.properties = _pf.properties
            nonlocal self
            self.dao.add(new_bean)
            pass

        def switch():
            nonlocal new_bean
            new_bean.properties.finish()

        def run_pos():
            nonlocal new_bean
            print(new_bean.properties.get(""))
            print(new_bean.properties.get(""))
            print(new_bean.url)

        new_bean = _MallPosBean(-1)
        new = Toplevel(self.root)
        new.title("添加项目")

        data_form = _MallPosForm(new, text="项目参数")
        data_form.new_data()
        data_form.pack(fill=X)

        _pf = _PropertiesForm(new, text="config.properties")
        _pf.new_config()

        #
        option_bar = Frame(new)
        switch = ttk.Button(option_bar, text="切换到此项目", command=switch)
        run = ttk.Button(option_bar, text="启动项目", command=run_pos)

        _pf.pack(side=TOP, fill=X)
        save = ttk.Button(new, text="保存", command=save)
        switch.pack(side=LEFT)
        run.pack(side=LEFT)
        option_bar.pack(side=BOTTOM)
        save.pack(side=BOTTOM, fill=X)

        new.bind("<Destroy>", self.refresh_data)
        center(new)
        # 置于最上层
        new.transient(self.root)
        # modal
        # new.grab_set()
        new.mainloop()
        pass

    def save_exit(self):

        self.root.quit()
        self.root.destroy()

    pass


class _MallPosForm(LabelFrame):

    def __init__(self, master=None, cnf={}, **kwargs):
        super().__init__(master, cnf, **kwargs)
        self.entry_map = {}

        self.name_entry = "名称"
        self.type_entry = "类型"
        self.url_entry = "项目地址"
        pass

    @property
    def name(self):
        return self.entry_map.get(self.name_entry).get()

    @property
    def type(self):
        return self.entry_map.get(self.type_entry).get()

    @property
    def url(self):
        return self.entry_map.get(self.url_entry).get()

    def add(self):
        return Frame(self)

    def new_data(self):
        container = self.add()
        form_fields = (self.name_entry, self.type_entry, self.url_entry)

        for field in form_fields:
            _container = Frame(container)
            caption_label = Label(_container, text=field, width=15)
            caption_label.pack(side=LEFT, padx=2, fill=X)

            _entry = ttk.Entry(_container)
            _entry.insert(0, "")
            _entry.pack(side=LEFT, padx=2)
            self.entry_map.update({field: _entry})
            _container.pack(side=TOP, fill=X, pady=4)
            pass

        container.pack(side=LEFT, fill=X, pady=4)
        pass

    def set_data(self, data):
        self.new_data()
        self.entry_map.get(self.name_entry).insert(0, data.name)
        self.entry_map.get(self.type_entry).insert(0, data.type)
        self.entry_map.get(self.url_entry).insert(0, data.url)
        pass

    pass


class _PropertiesForm(LabelFrame):

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
        self._path = None
        self._properties = None
        self._properties_edit = None
        pass

    @property
    def path(self):
        return self._path

    @property
    def properties(self):
        # 返回最新的
        _properties_str = self._properties_edit.get(1.0, END)
        self._properties = properties.loads(self._path, _properties_str.strip().split("\n"))
        return self._properties

    def new_config(self):
        def load_fn():
            nonlocal self
            self._path = askopenfilename(title=u'选择文件', initialdir=(os.path.expanduser(util.get_desktop_path())),
                                         filetypes=[("配置文件", ".properties",), ("文本文件", ".txt",)])
            self._load_config()
            pass

        load = ttk.Button(self, text="加载配置文件", command=load_fn)
        load.pack(side=BOTTOM, fill=X)
        pass

    def set_config(self, _path, _properties):
        self._path = _path
        self._properties = _properties

        if self._properties is None:
            self.new_config()
        else:
            self._properties_edit = Text(self)
            self._properties_edit.insert(END, "\n".join([_p for _p in self._properties.items()]))
            self._properties_edit.pack(side=TOP, fill=X)
        pass

    def _load_config(self):
        self._properties = properties.load(self._path)
        self._properties_edit = Text(self)
        self._properties_edit.insert(END, "\n".join([_p for _p in self._properties.items()]))
        self._properties_edit.pack(side=TOP, fill=X)
        pass


def center(tk):
    tk.update_idletasks()  # 刷新GUI
    w = tk.winfo_width()
    h = tk.winfo_height()
    sw = tk.winfo_screenwidth()
    sh = tk.winfo_screenheight()
    x, y = (sw - w) / 2, (sh - h) / 2
    tk.geometry("%dx%d+%d+%d" % (w, h, x, y))


def auto_login(connection_url, db_user, db_password, url):

    print(connection_url, db_user, db_password, url)
    pass


def mall_pos_manager():
    _MallPosUI()


pass

logger = logging.getLogger(__name__)
# mall_pos_manager()
if __name__ == '__main__':
    mall_pos_manager()
    pass
