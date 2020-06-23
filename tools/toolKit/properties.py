import pprint
import logging
import pathlib
import pickle


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

        if self.parent is not None:
            self.parent.child.append(self)
            pass

        if kwargs.get('child') is not None:
            self.child.append(kwargs.get('child'))
            pass

        if self.parent is not None:
            self.properties_items.extend(self.parent.properties_items)
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
        pass

        # id: {key : value} 不需要注释
        self.properties_map = {item.key: item.value for item in self.properties_items if
                               item.type == Properties.PropertiesItem.ITEM}

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
        config_properties = r'D:\apache-tomcat-7.0.41-windows-x64\apache-tomcat-7.0.41\webapps\Tech-Trans.Vaadin.esPOS61.MIS\WEB-INF\classes\config.properties'
        web_config_properties = r'D:\MallPosWorkSpace\Tech-Trans.Vaadin.esPOS61.MIS\WebContent.Tech-Trans.Vaadin.esPOS61.MIS\WEB-INF\classes\config.properties'

        # 每个配置唯一，有source和web_source两个属性。分别对应项目下的配置和发布到webapps下的配置。
        # 切换配置属性时，两个路径下的配置文件都需要切换。
        self.ini = {"pos61": {"source": config_properties, "web_source": web_config_properties}}

        logger.info("load source.ini...")

        # 格式为 {name:properties}
        self.properties_data = {}
        self.__read()

        # 配置文件根 最终配置文件的操作指向root
        self.root = None
        # 当前管理的配置
        self.cache = None
        pass

    def __check__(self):

        if self.cache is None:
            raise PropertiesException("no select Properties")
        pass

    def get(self, target):

        """读取并加载配置，加载完成可以进行其他操作, 根据target从ini找。"""
        _source = self.ini.get(target).get('source')
        self.cache = Properties(path=_source)
        logger.info('select properties %s.', self.cache.name)

        return self
        pass

    def list(self):
        self.__check__()

        for k in self.properties_data.keys():

            print(k, end=' - ')
        pass

    def copy(self, **kwargs):

        self.__check__()
        """
        ::kwargs name
        对当前加载的配置文件创建一个副本，替换其中的某些属性。可以对配置直接切换到某个副本。
        副本是当前设置的配置文件的子节点
        --keys 需要更新的keys
        --values 需要更新的values
        """
        _clone_name = kwargs.get('name')
        _keys = kwargs.get('keys')
        _values = kwargs.get('values')
        _clone = Properties(parent=self.cache)
        _clone.name = _clone_name

        for k, v in zip(_keys, _values):
            _clone.update(k, v)
        pass

        # 保存节点
        self.properties_data.update({_clone.name: _clone})

        #
        self.cache = _clone
        return self
        pass

    def update(self, **kwargs):

        """ ::kwargs --user = DATABASEUSER --pwd = DATABASEPASSWORD 数据库用户名密码不同，使用该选项
        --df = DATABASE 数据库用户密码相同，使用该选项。优先取 --def

        """
        if kwargs.get('df') is not None:
            self.switch(keys=('DatabaseUser', 'DatabasePassword',), values=(kwargs['df'], kwargs['df'],))
        else:
            self.switch(keys=('DatabaseUser', 'DatabasePassword',), values=(kwargs['user'], kwargs['pwd'],))
        pass

    def update(self, **kwargs):

        """ ::kwargs --user = DATABASEUSER --pwd = DATABASEPASSWORD 数据库用户名密码不同，使用该选项
        --df = DATABASE 数据库用户密码相同，使用该选项。优先取 --def

        """
        if kwargs.get('df') is not None:
            self.switch(keys=('DatabaseUser', 'DatabasePassword',), values=(kwargs['df'], kwargs['df'],))
        else:
            self.switch(keys=('DatabaseUser', 'DatabasePassword',), values=(kwargs['user'], kwargs['pwd'],))
        pass

    def switch(self, **kwargs):

        """::kwargs name 切换到当前的配置文件"""
        self.__check__()

        _keys = kwargs.get('keys')
        _values = kwargs.get('values')
        for k, v in zip(_keys, _values):
            self.cache.update(k, v)
            pass

        source = self.ini.get(self.cache.name).get('source')
        logger.info('switch %s resource properties %s.', self.cache.name, source)
        web_source = self.ini.get(self.cache.name).get('web_source')
        logger.info('switch %s to web source properties %s.', self.cache.name, web_source)

        with open(source, 'w', encoding='utf-8') as file:
            file.writelines(str(self.cache))
        pass

        with open(web_source, 'w', encoding='utf-8') as file:
            file.writelines(str(self.cache))
        pass

    def __read(self):

        # 数据持久化
        try:
            with open(pathlib.Path.cwd().joinpath('properties/data.pkl'), 'rb') as file:
                self.properties_data = pickle.load(file)
                pass
        except:
            logger.warning('data.pkl is not found.')
            pass
        pass

    def __str__(self):

        # 数据持久化
        with open(pathlib.Path.cwd().joinpath('properties/data.pkl'), 'wb') as file:
            pickle.dump(self.properties_data, file)
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

try:
    manager = PropertiesManager()
    manager.get(target="pos61").switch_database(df='MD61_RYG')
except PropertiesException as e:
    logger.error(e.message)
    pass
finally:
    print(manager)
