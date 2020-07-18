import pprint
import logging
import pathlib
import pickle
import configparser as parser


class Properties:
    class PropertiesItem:
        ITEM, COMMENT = 'ITEM', 'COMMENT'

        def __init__(self):
            self.type = Properties.PropertiesItem.ITEM
            self.key = None
            self.value = None
            pass

        def __str__(self):
            return "{}={}\n".format(self.key,
                                    self.value) if self.type == Properties.PropertiesItem.ITEM else "#{}".format(
                self.key)

        def is_item(self):

            self.type == Properties.PropertiesItem.ITEM
            pass

        def is_comment(self):

            self.type == Properties.PropertiesItem.COMMENT
            pass

        def refresh(self, data_map):

            self.value = data_map.get(self.key) if data_map.get(self.key) is not None else None
            return self
            pass

        @staticmethod
        def comment(_input):
            _r = Properties.PropertiesItem()
            _r.type = Properties.PropertiesItem.COMMENT
            _r.key = _input
            return _r

        @staticmethod
        def item(_key, _value):
            _r = Properties.PropertiesItem()
            _r.type = Properties.PropertiesItem.ITEM
            _r.key = _key
            _r.value = _value
            return _r

        @staticmethod
        def analyze(_properties_value: str):
            if _properties_value[0] == '#':
                return Properties.PropertiesItem.comment(_properties_value[1:])
            else:

                _data = _properties_value.split('=')
                return Properties.PropertiesItem.item(_data[0], _data[1]) if 0 < len(_data) >= 2 else None

        pass

    def __init__(self, **kwargs):

        self.__name = None
        self.child = []
        self.parent = kwargs.get('parent')  # Type: Properties 父级配置
        self.properties_items = []
        self.properties_map = {}

        if self.parent is not None:
            self.parent.child.append(self)
            pass

        if kwargs.get('child') is not None:
            self.child.append(kwargs.get('child'))
            pass

        if self.parent is not None:
            self.properties_items.extend(self.parent.properties_items)
            self.properties_map.update(self.parent.properties_map)
            pass

        # [propertiesItem,...]
        if kwargs.get('path') is not None:
            with open(kwargs.get('path'), 'r', encoding='UTF-8') as p:
                for _i in p.readlines():
                    self.properties_items.append(Properties.PropertiesItem.analyze(_i))
                pass

            while None in self.properties_items:
                self.properties_items.remove(None)
                pass
            # id: {key : value} 不需要注释
            self.properties_map.update({item.key: item.value for item in self.properties_items if
                                        item.type == Properties.PropertiesItem.ITEM})
        pass

    def update(self, key, value):

        self.properties_map.update({key: value})

    def target(self):

        return "\t\n" + self.parent.target() if self.parent is not None else ""

    @property
    def name(self):

        return self.__name

    @name.getter
    def name(self):

        return self.__name
        pass

    @name.setter
    def name(self, value):

        self.__name = value
        pass

    def __str__(self):

        # 按propertiesItem的顺序来打印
        fn_check_properties = lambda _item: _item if _item.is_comment() else _item.refresh(self.properties_map)
        return "".join([str(fn_check_properties(i)) for i in self.properties_items])

    pass


class PropertiesException(Exception):

    def __init__(self, message):
        self.message = message
        pass

    pass


class PropertiesManager:

    def __init__(self):

        # 加载根配置文件的配置
        self.sql_server_connection_url_temp = None
        # 配置文件根 最终配置文件的操作指向root
        self.root = None
        # 当前管理的配置
        self.cache = None

        self.ini = {}
        self.__read_ini()
        # 格式为 {name:properties}
        self.properties_data = {}
        self.properties_tree = {}
        self.__read()
        pass

    def __read_ini(self):

        _conn = parser.ConfigParser()
        _path = pathlib.Path.cwd().joinpath('properties/source.ini')
        _conn.read(_path, encoding='UTF-8')
        self.sql_server_connection_url_temp = dict(_conn.items('DEFAULT')).get('databaseconnectionurl')
        sections = _conn.sections()
        for section in sections:
            self.ini.update({section: dict(_conn.items(section))})
        # 每个配置唯一，有source和web_source两个属性。分别对应项目下的配置和发布到webapps下的配置。
        # 切换配置属性时，两个路径下的配置文件都需要切换。

        logger.info("load properties ini...")
        pass

    def __check__(self):

        if self.root is None:
            raise PropertiesException("no select Properties")
        pass

    def select(self, target):

        """加载根配置文件，一切修改都在该配置文件上。"""
        try:
            self.ini[target]

            # 如果缓存中没有
            if self.properties_data.get(target) is None:
                _source = self.ini.get(target).get('source')
                self.root = Properties(path=_source)
                self.root.name = target
                logger.info('first select properties %s.', self.root.name)
            else:
                self.root = self.properties_data.get(target)
                logger.info('select properties %s.', self.root.name)

            self.cache = self.root
        except KeyError:

            logger.error("no root in target. maybe 'get'?")
            pass
        return self
        pass

    def get(self, target):

        """获取配置"""
        self.__check__()

        self.cache = self.properties_data[target]
        logger.info('get properties %s.', self.cache.name)

        # print(str(self.cache))
        return self
        pass

    def list(self):
        """显示当前配置文件的子级。"""
        self.__check__()
        logger.info("{} list: {}".format(self.cache.name, self.properties_tree.get(self.cache.name)))
        return self
        pass

    def all_list(self):
        """显示所有配置文件。"""
        self.__check__()
        logger.info("{} list: {}".format(self.root.name, self.properties_tree))
        return self
        pass

    def clone(self, **kwargs):

        self.__check__()
        """
        ::kwargs name
        对当前加载的配置文件创建一个副本，替换其中的某些属性。可以对配置直接切换到某个副本。
        副本是当前设置的配置文件的子节点
        --keys 需要更新的keys
        --values 需要更新的values
        """
        _clone_name = kwargs['name']
        _keys = kwargs.get('keys')
        _values = kwargs.get('values')
        _clone = Properties(parent=self.cache)
        _clone.name = _clone_name

        if bool(_keys and _values):
            for k, v in zip(_keys, _values):
                _clone.update(k, v)
            pass

        # 保存节点
        self.properties_data.update({_clone.name: _clone})
        # 先将clone的添加到当前配置文件的子级，再切换配置文件
        _trees = self.properties_tree.get(self.cache.name)
        _trees.add(_clone.name)
        self.properties_tree.update({self.cache.name: _trees})
        # 切换
        self.cache = _clone
        self.properties_tree.update({self.cache.name: set()})
        return self
        pass

    def clone_db(self, name, user):

        """clone的同时，更新数据库用户名和密码，更新ApplicationTitle配置，为项目#name版本#root"""
        kwargs = {"name": name, "keys": ('DatabaseUser', 'DatabasePassword', 'ApplicationTitle',),
                  "values": (user, user, "项目{},版本{}".format(name, self.root.name),)}
        return self.clone(**kwargs)
        pass

    def clone_db_ss(self, name, user):
        """clone的同时，更新sqlserver数据库用户名和密码，更新ApplicationTitle配置，为项目#name版本#root"""
        kwargs = {"name": name, "keys": ('DatabaseConnectionUrl', 'ApplicationTitle',),
                  "values": (
                      self.sql_server_connection_url_temp.format(user), "项目{},版本{}".format(name, self.root.name),)}
        return self.clone(**kwargs)
        pass

    def switch_db(self, user):

        """切换数据库的账号密码为user，同时更新ApplicationTitle配置，为项目#user版本#root"""
        self.switch(keys=('DatabaseUser', 'DatabasePassword', 'ApplicationTitle',),
                    values=(user, user, "项目{},版本{}".format(user, self.root.name),))
        pass

    def switch_db_ss(self, user):

        """切换sqlserver数据库为user，同时更新ApplicationTitle配置，为项目#user版本#root"""
        self.switch(keys=('DatabaseConnectionUrl', 'ApplicationTitle',),
                    values=(
                        self.sql_server_connection_url_temp.format(user),
                        "SQLSERVER.项目{},版本{}".format(user, self.root.name),))
        pass

    def remove(self, target):

        """删掉配置"""
        self.properties_data.pop(target)
        self.properties_tree.get(self.cache.name).remove(target)
        self.properties_tree.pop(target)
        return self
        pass

    def switch(self, **kwargs):

        """::kwargs name 切换到当前的配置文件"""
        self.__check__()

        _keys = kwargs.get('keys')
        _values = kwargs.get('values')

        if bool(_keys and _values):
            for k, v in zip(_keys, _values):
                self.cache.update(k, v)
                pass

        source = self.ini.get(self.root.name).get('source')
        logger.info('switch %s resource properties %s.', self.cache.name, source)
        web_source = self.ini.get(self.root.name).get('web_source')
        logger.info('switch %s to web source properties %s.', self.cache.name, web_source)

        # print(str(self.cache))
        with open(source, 'w', encoding='utf-8') as file:
            file.writelines(str(self.cache))
        pass

        with open(web_source, 'w', encoding='utf-8') as file:
            file.writelines(str(self.cache))
        return self
        pass

    def update(self, **kwargs):

        """更新配置"""
        self.__check__()
        _keys = kwargs.get('keys')
        _values = kwargs.get('values')

        if bool(_keys and _values):
            for k, v in zip(_keys, _values):
                self.cache.update(k, v)
                pass
        logger.info("update properties success.")
        return self
        pass

    def __init_data(self):

        """第一次使用， 初始化数据。"""

        def _properties(name, path):
            _p = Properties(path=path)
            _p.name = name
            return _p
            pass

        self.properties_data.update({k: _properties(k, v.get('source')) for k, v in self.ini.items()})
        self.properties_tree.update({k: set() for k in self.ini.keys()})
        pass

    def __read(self):

        # 数据持久化
        try:
            with open(pathlib.Path.cwd().joinpath('properties/data.pkl'), 'rb') as file:
                self.properties_data = pickle.load(file)
                pass

            with open(pathlib.Path.cwd().joinpath('properties/tree.pkl'), 'rb') as file:
                self.properties_tree = pickle.load(file)
                pass
        except:

            logger.warning('data.pkl is not found.')
            self.__init_data()
            pass
        pass

    def show(self):
        print(str(self.cache))

    def __str__(self):

        # 数据持久化
        with open(pathlib.Path.cwd().joinpath('properties/data.pkl'), 'wb') as file:
            pickle.dump(self.properties_data, file)
            pass
        with open(pathlib.Path.cwd().joinpath('properties/tree.pkl'), 'wb') as file:
            pickle.dump(self.properties_tree, file)
            pass
        return 'Job Done'
        pass


# properties get pos61
# ini
# [POS61]
# source = D:/a.properties
# web_source = D:/tomcat/a/a.properties

def names(p):
    if p.child is None or len(p.child) <= 0:
        yield p.name

    for _c in p.child:
        yield from "{}：{}".format(_c.name, str(names(_c)))

    pass


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# {'pos61' : ['oracle', 'sqlserver'], 'oracle' : ['bhgc', 'ryg'], 'sqlserver' : ['sjh']}
# properties get pos61 switch BHGC

if __name__ == '__main__':
    try:
        manager = PropertiesManager()
        manager.select('POS61').get('ora100').get('sqlserver').clone_db_ss('T1', 'T1').show()

    except PropertiesException as e:
        logger.error(e.message)
        pass
    finally:
        print(manager)
