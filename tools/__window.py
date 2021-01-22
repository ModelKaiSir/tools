import sqlite3
from tkinter import *
from tkinter.ttk import *

"""一系列带界面的小工具"""
"""科传项目管理工具"""


def mall_pos_manager():
    def add_mall_pos():
        print("1111111")
        pass

    def load_mall_pos(_cols):
        _tree = Treeview(table_frame, column=_cols)
        for _c in _cols:
            _tree.heading(_c, text=_c)
            _tree.column(_c, anchor=S)

        _tree.insert('', END, values=("世贸商城", "Oracle", "localhost:8080"))
        _tree.insert('', END, values=("世贸商城2", "Oracle", "localhost:8080"))
        _tree.insert('', END, values=("世贸商城3", "Oracle", "localhost:8080"))
        _tree.insert('', END, values=("世贸商城4", "Oracle", "localhost:8080"))
        _tree.pack()
        pass

    root = Tk()
    menu_bar = Menu(root, tearoff=0)

    menu = Menu(menu_bar)
    menu.add_command(label="New", command=add_mall_pos)
    menu.add_command(label="Quit", command=root.quit)
    menu_bar.add_cascade(label="Option", menu=menu)

    toolbar_frame = Frame(root)
    table_frame = Frame(root)
    btn2 = Button(toolbar_frame, text="复制")
    btn2.pack(padx=2, side=LEFT)

    root.title("mall_pos_manager")
    root.config(menu=menu_bar)

    load_mall_pos(["名称", "数据库类型", "项目地址"])
    toolbar_frame.pack(side=TOP, pady=5)
    table_frame.pack(side=LEFT, padx=2, pady=5)
    root.mainloop()
    pass


mall_pos_manager()
