# 数据脚本工具
import sql_server_connection as ssc
import oracle_connection as oc
import abc

"""
表信息、字段信息
"""

START_SQL_LABEL, END_SQL_LABEL = "/*<SQL>*/", "/*</SQL>*/"


class Config:

    def __init__(self):
        self.appendLabel = False
        self.sqlLabel = START_SQL_LABEL + "\n{}\n" + END_SQL_LABEL
        self.connection_url = "jdbc:oracle:thin:@172.31.2.100:1521:ORA100"
        self.database_user = "MD65_MDD"
        self.database_password = "MD65_MDD"


CONFIG = Config()


class Column:

    def __init__(self, _table):
        """

        字段信息
        :param _table:
        """
        self.table = _table
        self.name = None
        self.type = None
        self.primary = False
        self.nullable = True
        self.comments = None
        self.default = None
        self.dataLength = 0
        pass

    @staticmethod
    def of(_table, **kwargs):
        """

        :param _table:
        :param kwargs: name type primary nullable comments def
        :return:
        """
        _result = Column(_table)
        _result.name = kwargs.get('name')
        _result.type = kwargs.get('type')
        _result.primary = bool(kwargs.get('primary'))
        _result.nullable = bool(kwargs.get('nullable'))
        _result.comments = kwargs.get('comments')
        _result.default = kwargs.get('default')
        _result.dataLength = kwargs.get('len')
        return _result


class Table(abc.ABC):

    def __init__(self, _table_name):
        """
        表信息，包括表名，表注释和字段信息
        :param _table_name:
        """
        self.comments = None
        self.__table_name = _table_name
        self.__column = None  # type:Column

    @abc.abstractmethod
    def get(self): pass

    def __str__(self):
        return self.__table_name

    pass


class OracleTable(Table):

    def __init__(self, _table_name):
        Table.__init__(self, _table_name)
        pass

    def get(self):
        _query = """
        SELECT T.TABLE_NAME,
               C.COMMENTS,
               T1.COLUMN_NAME,
               CASE
                 WHEN CONS.POSITION IS NULL THEN
                  0
                 ELSE
                  1
               END PRIMARYKEY,
               T1.DATA_TYPE,
               T1.DATA_DEFAULT,
               CASE
                 WHEN T1.NULLABLE = 'N' THEN
                  0
                 ELSE
                  1
               END NULLABLE,
               T2.COMMENTS,
               T1.DATA_LENGTH
          FROM USER_TABLES T
          LEFT JOIN USER_TAB_COLUMNS T1
            ON T.TABLE_NAME = T1.TABLE_NAME
          LEFT JOIN USER_CONS_COLUMNS CONS
            ON T1.TABLE_NAME = CONS.table_name
           AND T1.COLUMN_NAME = CONS.column_name
           AND CONS.POSITION IS NOT NULL
          LEFT JOIN USER_COL_COMMENTS T2
            ON T1.COLUMN_NAME = T2.COLUMN_NAME
           AND T1.TABLE_NAME = T2.TABLE_NAME, USER_TAB_COMMENTS C
         WHERE T.TABLE_NAME = C.table_name
           AND T.TABLE_NAME = :tablename
         ORDER BY T1.COLUMN_ID"""

        __connection = oc \
            .OracleConnection.connection_url_of(CONFIG.connection_url, CONFIG.database_user)

        with oc.OracleConnectionManager(__connection) as m:
            _rows = m.query(_query, _data={"tablename": str(self)})

            for _row in _rows:
                yield Column.of(self, name=_row[2], primary=int(_row[3]), type=_row[4], default=_row[5],
                                nullable=_row[6], comments=_row[7], len=_row[8])
        pass


class SqlServerTable(Table):

    def get(self):
        _query = """
        SELECT
          T.TABLE_NAME,
          ''  COMMENTS,
          T.COLUMN_NAME,
          CASE
          WHEN PK.ORDINAL_POSITION IS NOT NULL
            THEN
              1
          ELSE
            0
          END PRIMARYKEY,
          T.DATA_TYPE,
          T.COLUMN_DEFAULT,
          CASE
          WHEN T.IS_NULLABLE = 'YES'
            THEN
              1
          ELSE
            0
          END NULLABLE,
          TABLE_COMMENTS.COLUMN_DESCRIPTION,
          T.CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS T
          LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE PK
            ON T.TABLE_NAME = PK.TABLE_NAME
               AND T.COLUMN_NAME = PK.COLUMN_NAME
          LEFT JOIN (SELECT
                       A.NAME                        AS TABLE_NAME,
                       B.NAME                        AS COLUMN_NAME,
                       cast(C.VALUE AS VARCHAR(500)) AS COLUMN_DESCRIPTION
                     FROM SYS.TABLES A
                       INNER JOIN SYS.COLUMNS B
                         ON B.OBJECT_ID = A.OBJECT_ID
                       LEFT JOIN SYS.EXTENDED_PROPERTIES C
                         ON C.MAJOR_ID = B.OBJECT_ID
                            AND C.MINOR_ID = B.COLUMN_ID
                     WHERE A.NAME = %s) TABLE_COMMENTS
            ON T.TABLE_NAME = TABLE_COMMENTS.TABLE_NAME
               AND T.COLUMN_NAME = TABLE_COMMENTS.COLUMN_NAME
        WHERE T.TABLE_NAME = %s
        ORDER BY T.ORDINAL_POSITION"""

        __connection = ssc \
            .SqlServerConnection.connection_url_of(CONFIG.connection_url, CONFIG.database_user,
                                                   CONFIG.database_password)

        with ssc.SqlServerConnectionManager(__connection) as m:
            _rows = m.query(_query, _data=(str(self), str(self),))

            for _row in _rows:
                yield Column.of(self, name=_row[2], primary=int(_row[3]), type=_row[4], default=_row[5],
                                nullable=_row[6], comments=_row[7], len=_row[8])
        pass


"""
注释转换
"""


class CommentStructure(abc.ABC):

    def __init__(self):
        abc.ABC.__init__(self)
        pass

    @abc.abstractmethod
    def convert(self, _table):
        # do something
        pass

    pass


class OracleCommentStructure(CommentStructure):

    def convert(self, _table: Table):
        """
        转换为oracle数据库的表注释语句。
        :param _table: 表信息
        :return:
        """

        __template = "COMMENT ON TABLE {} IS '{}';"
        __template_column = "COMMENT ON COLUMN {table}.{column} IS '{comments}';"

        _result = list()

        if bool(_table.comments):
            _result.append(__template.format(_table, _table.comments))
            pass

        for _column in _table.get():

            if _column.comments is not None:

                if not CONFIG.appendLabel:
                    _str = __template_column.format(table=_table, column=_column.name, comments=_column.comments)
                else:
                    _str = __template_column.format(table=_table, column=_column.name, comments=_column.comments)
                    _str = CONFIG.sqlLabel.format(_str)

                _result.append(_str)
        return _result
        pass

    pass


class SqlServerCommentStructure(CommentStructure):

    def convert(self, _table: Table):
        """
        转换为oracle数据库的表注释语句。
        :param _table: 表信息
        :return:
        """

        __template = "sq ON TABLE {} IS '{}';"
        __template_column = """EXEC sys.sp_addextendedproperty
        @name=N'MS_Description',
        @level0type=N'SCHEMA',@level0name=N'dbo',
        @level1type=N'TABLE',@level2type=N'COLUMN',
        @level1name=N'{table}', @level2name=N'{column}',@value=N'{comments}';"""

        _result = list()

        if bool(_table.comments):
            _result.append(__template.format(_table, _table.comments))
            pass

        for _column in _table.get():

            if _column.comments is not None:

                if not CONFIG.appendLabel:
                    _str = __template_column.format(table=_table, column=_column.name, comments=_column.comments)
                else:
                    _str = __template_column.format(table=_table, column=_column.name, comments=_column.comments)
                    _str = CONFIG.sqlLabel.format(_str)

                _result.append(_str)
        return _result
        pass


"""表结构转换"""


class TableStructure(abc.ABC):

    @abc.abstractmethod
    def convert(self, _table: Table):
        pass

    @staticmethod
    def convert_data_type(target, _col: Column):

        try:
            for k, v in DATA_TYPE.items():

                if not isinstance(v, list):
                    continue
                if v.count(_col.type.upper()) > 0:

                    if k == "STR":
                        return DATA_TYPE.get(k + "-CONVERT")[target].format(LENGTH_CONVERT[target](_col.dataLength))
                    else:
                        return DATA_TYPE.get(k + "-CONVERT")[target]
                    pass
                pass

            return _col.type
        except KeyError:

            # 不存在则直接返回
            return _col.type
            pass
        pass

    pass


class OracleTableStructure(TableStructure):

    def convert(self, _table: Table):

        _start = "CREATE TABLE {} ("
        _end = ")"

        _result = list()
        _pks = list()

        _trigger = False
        _result.append(START_SQL_LABEL) if CONFIG.appendLabel else None
        _result.append(_start.format(str(_table)))

        for _col in _table.get():  # type:Column

            if _col.primary:
                _pks.append(_col.name)
                pass

            _trigger = True if DEFAULT_TRIGGER_COLUMNS.count(_col.name) > 0 else _trigger

            _result.append("\t" + " ".join(
                [_col.name, TableStructure.convert_data_type(ORACLE, _col), "not null" if not _col.nullable else "",
                 ","]))
            pass

        # 去掉最后一个字段结尾的逗号
        _result[-1] = _result[-1][:-1]
        _result.append(_end)
        _result.append(END_SQL_LABEL) if CONFIG.appendLabel else None

        _result.append(START_SQL_LABEL) if CONFIG.appendLabel else None
        _result.append(
            "ALTER TABLE ADD CONSTRAINT {}_PK PRIMARY KEY({}) USING INDEX TABLESPACE INDEX01;".format(str(_table),
                                                                                                      ",".join(_pks)))
        _result.append(END_SQL_LABEL) if CONFIG.appendLabel else None
        _result.append("-- 触发器自行转换")

        if _trigger:
            _result.extend(oracle_trigger(str(_table)))
        return _result
        pass


class SqlServerTableStructure(TableStructure):

    def convert(self, _table: Table):
        _start = "CREATE TABLE {} ("
        _end = ")"

        _result = list()
        _pks = list()

        _trigger = False
        _result.append(START_SQL_LABEL) if CONFIG.appendLabel else None
        _result.append(_start.format(str(_table)))

        for _col in _table.get():  # type:Column

            if _col.primary:
                _pks.append(_col.name)
                pass

            _trigger = True if DEFAULT_TRIGGER_COLUMNS.count(_col.name) > 0 else _trigger

            _result.append("\t" + " ".join(
                [_col.name, TableStructure.convert_data_type(SQL_SERVER, _col), "not null" if not _col.nullable else "",
                 ","]))
            pass

        if _pks == 0:
            # 去掉最后一个字段结尾的逗号
            _result[-1] = _result[-1][:-1]
        else:

            _result.append("CONSTRAINT {}_PK PRIMARY KEY({})".format(str(_table), ",".join(_pks)))

        _result.append(_end)
        _result.append(END_SQL_LABEL) if CONFIG.appendLabel else None
        _result.append("GO")
        _result.append("-- 默认触发器")

        if _trigger:
            _result.extend(sql_server_trigger(str(_table), _primary_keys=_pks))
        return _result
        pass

    pass


"""
全局变量 参数配置
"""
ORACLE, SQL_SERVER = "ORACLE", "SQL_SERVER"

DATA_TYPE = {
    "STR": ["VARCHAR2", "NVARCHAR2", "NVARCHAR"],
    "NUMBER": ["NUMBER", "DECIMAL"],
    "DATE": ["DATE", "DATETIME"],
    "STR-CONVERT": {ORACLE: "VARCHAR2({})", SQL_SERVER: "NVARCHAR({})"},
    "NUMBER-CONVERT": {ORACLE: "NUMBER(16, 4)", SQL_SERVER: "DECIMAL(16, 4)"},
    "DATE-CONVERT": {ORACLE: "DATE", SQL_SERVER: "DATETIME"}
}

# sql server 数据库字段长度要除以3 oracle数据库字段长度要乘以3
LENGTH_CONVERT = {

    ORACLE: lambda _i: _i * 3, SQL_SERVER: lambda _i: int(_i / 3)
}

DATABASE = {

    ORACLE: oc.OracleConnectionManager,
    SQL_SERVER: ssc.SqlServerConnectionManager
}

COMMENT_STRUCTURE = {

    ORACLE: OracleCommentStructure,
    SQL_SERVER: SqlServerCommentStructure
}

TABLE_STRUCTURE = {

    ORACLE: OracleTableStructure,
    SQL_SERVER: SqlServerTableStructure
}

DEFAULT_TRIGGER_COLUMNS = ["XF_LASTMODTIME"]


def sql_server_trigger(_table_name, _primary_keys):
    _template = """CREATE TRIGGER {}
     ON {}
    AFTER INSERT, UPDATE
    AS
     BEGIN
        UPDATE {}
            SET XF_LASTMODTIME = GETDATE()
             WHERE EXISTS(SELECT 1 FROM {} B WHERE {});
    END"""

    _result = list()

    clauses = "".join(["B.{} = {}".format(p.strip(), p.strip()) for p in _primary_keys])
    _result.append(
        CONFIG.sqlLabel.format(_template.format(_table_name + "_INS", _table_name, _table_name, "INSERTED", clauses)))
    _result.append("GO")
    _result.append(
        CONFIG.sqlLabel.format(_template.format(_table_name + "_UP", _table_name, _table_name, "UPDATED", clauses)))
    _result.append("GO")

    return _result
    pass


def oracle_trigger(_table_name):

    _template = """CREATE OR REPLACE TRIGGER {}
        BEFORE {} ON {}
        FOR EACH ROW
    BEGIN
        :NEW.XF_LASTMODTIME := SYSDATE;
    END {};"""

    _result = list()

    _result.append(
        CONFIG.sqlLabel.format(_template.format(_table_name + "_INS", "INSERT", _table_name, _table_name + "_INS")))
    _result.append("/")
    _result.append(
        CONFIG.sqlLabel.format(_template.format(_table_name + "_UP", "UPDATE", _table_name, _table_name + "_UP")))
    _result.append("/")

    return _result
    pass


# 实现简单的触发器 TECHTRANS对 XF_LASTMODTIME 进行自动赋值
TABLE = {

    ORACLE: OracleTable,
    SQL_SERVER: SqlServerTable
}


def convert_comments_structure(_source_database_name, _target_database_name, _table_name):
    """
    转换数据库表注释到目标数据库
    :param _target_database_name: 转换到目标数据库格式
    :param _table_name:
    :param _source_database_name: 需要转换的来源数据库格式
    :return:
    """

    _result = COMMENT_STRUCTURE[_target_database_name]().convert(TABLE[_source_database_name](_table_name))
    return _result
    pass


def convert_table_structure(_source_database_name, _target_database_name, _table_name):
    """
    转换数据库表结构到目标数据库
    :param _target_database_name: 转换到目标数据库格式
    :param _table_name:
    :param _source_database_name: 需要转换的来源数据库格式
    :return:
    """

    _result = TABLE_STRUCTURE[_target_database_name]().convert(TABLE[_source_database_name](_table_name))
    return _result
    pass


if __name__ == '__main__':

    CONFIG.appendLabel = True
    CONFIG.connection_url = "jdbc:oracle:thin:@172.31.2.100:1521:ORA100"
    CONFIG.database_user = "MD61_RAXH"
    CONFIG.database_password = "MD61_RAXH"

    # for i in convert_table_structure(SQL_SERVER, ORACLE, "XF_MDCONTRACTH"):
    #     print(i)
    #     pass
    for i in convert_table_structure(ORACLE, SQL_SERVER, "XF_MDTENDERGROUP"):
        print(i)
        pass
    pass
