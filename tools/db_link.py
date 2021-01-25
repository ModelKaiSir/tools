import abc
import logging
import cx_Oracle
import pymssql


class DbDriver:

    def __init__(self):
        self.ip = None
        self.port = None
        self.user = None
        self.pwd = None
        self.db_name = None

    pass


class DbLink(abc.ABC):

    @abc.abstractmethod
    def __init__(self, driver: DbDriver):
        self.driver = driver
        self.connection = None
        pass

    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abc.abstractmethod
    def query(self, sql, parameters):
        pass

    @abc.abstractmethod
    def update(self, sql, parameters):
        pass


class OracleDbLink(DbLink):

    def __init__(self, driver: DbDriver):
        """Oracle db link
        :param driver db info
        CONNECTION URL -> USER/PWD@IP:PORT/DB_NAME"""
        super().__init__(driver)
        pass

    def __enter__(self):

        self.connection = \
            cx_Oracle.connect(
                f"{self.driver.user}/{self.driver.pwd}@{self.driver.ip}:{self.driver.port}/{self.driver.db_name}")
        return self
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.connection is not None
        self.connection.close()
        logger.info("connection close")
        pass

    def query(self, sql, parameters=None):
        """
        :param sql -> select * from table where col = :key
        :param parameters -> {key:value}"""
        assert self.connection is not None
        cursor = self.connection.cursor()

        logger.debug(f"oracle link : {sql}")
        logger.debug(f"parameter = {parameters}")

        if parameters is not None:
            cursor.prepare(sql)
            cursor.execute(None, parameters)
        else:
            cursor.execute(sql)

        _result = cursor.fetchall()

        cursor.close()
        return _result
        pass

    def update(self, sql, parameters):
        """
        :param sql -> update table ... where col = :key
        :param parameters -> {key:value}"""
        assert self.connection is not None
        cursor = self.connection.cursor()

        logger.debug(f"oracle link : {sql}")
        logger.debug(f"parameter = {parameters}")

        if parameters is not None:
            cursor.prepare(sql)
            cursor.execute(None, parameters)
        else:
            cursor.execute(sql)

        self.connection.commit()

        cursor.close()
        return cursor.rowcount
        pass


class SqlServerDbLink(DbLink):

    def __init__(self, driver: DbDriver):
        """
        SqlServer db link
        :param driver db info"""
        super().__init__(driver)
        pass

    def __enter__(self):
        self.connection = pymssql.connect(self.driver.ip, self.driver.user, self.driver.pwd, self.driver.db_name)
        return self
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.connection is not None
        self.connection.close()
        logger.info("connection close")
        pass

    def query(self, sql, parameters=None):
        """
        :param sql -> select * from table where col = %s
        :param parameters -> (value,)"""
        logger.debug(f"SqlServer link : {sql}")
        logger.debug(f"parameter = {parameters}")
        cursor = self.connection.cursor()

        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, parameters)
        return cursor.fetchall()
        pass

    def update(self, sql, parameters=None):
        """
        :param sql -> update table ... where col = %s
        :param parameters -> (value,)"""
        logger.debug(f"SqlServer link : {sql}")
        logger.debug(f"parameter = {parameters}")
        cursor = self.connection.cursor()

        if parameters is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, parameters)

        self.connection.commit()
        return cursor.rowcount
        pass


def parse_properties() -> DbDriver:
    """解析properties文件返回DbDriver"""
    import configparser as parser

    driver = DbDriver()
    DatabaseDriver = None
    DatabaseConnectionUrl = None
    DatabaseUser = None
    DatabasePassword = None
    del parser
    return driver
    pass


ip: str = None
port: str = None
db_name: str = None


def __parse_oracle_connection_url(url) -> (ip, port, db_name):
    """jdbc:oracle:thin:@{ip}:{port}:{db_name} -> [ip, port, db_name]
    :param url Oracle DatabaseConnectionUrl"""
    r = str(url).replace("jdbc:oracle:thin:@", "").split(":")
    return r
    pass


def __parse_sqlserver_connection_url(url) -> (ip, port, db_name):
    """jdbc:sqlserver://172.31.2.100:1433;DatabaseName=TEST; SA ORA100-> ['172.31.2.100', 'SA', 'ORA100', 'TEST']
    param url SqlServer DatabaseConnectionUrl"""
    p = str(url).replace("jdbc:sqlserver://", "").split(";")
    ip, port = p[0].split(":")
    db_name = p[1].split("=")[-1]
    return ip, port, db_name
    pass


ORACLE_DRIVER = "oracle.jdbc.driver.OracleDriver"
SQLSERVER_DRIVER = "com.microsoft.sqlserver.jdbc.SQLServerDriver"

ANALYSIS_URL = {
    "ORACLE": __parse_oracle_connection_url,
    "SQLSERVER": __parse_sqlserver_connection_url,
    ORACLE_DRIVER: __parse_oracle_connection_url,
    SQLSERVER_DRIVER: __parse_sqlserver_connection_url
}

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def open_link(driver, connection_url, user, pwd):
    _links = ANALYSIS_URL[driver](connection_url)
    _driver = DbDriver()
    _driver.ip, _driver.port, _driver.db_name = _links
    _driver.user, _driver.pwd = user, pwd
    if driver == ORACLE_DRIVER:
        return OracleDbLink(_driver)
    elif driver == SQLSERVER_DRIVER:
        return SqlServerDbLink(_driver)
    pass


def __test__():
    help(OracleDbLink)
    help(SqlServerDbLink)
    # _links = parse_sqlserver_connection_url("jdbc:sqlserver://172.31.2.100:1433;DatabaseName=MD61_HNXM;")
    _links = ANALYSIS_URL[ORACLE_DRIVER]("jdbc:oracle:thin:@172.31.2.100:1521:ORA100")
    _driver = DbDriver()
    _driver.ip, _driver.port, _driver.db_name = _links

    _driver.user = "MD61_RAXH"
    _driver.pwd = "MD61_RAXH"

    with OracleDbLink(_driver) as db:
        print(db.update("UPDATE XF_STAFF SET XF_NAME = '佳洁口腔2' WHERE XF_STAFFCODE = :A", {"A": "0082"}))
        pass

    _driver.db_name = "MD61_HNXM"
    _driver.user = "SA"
    _driver.pwd = "ORA100"
    with SqlServerDbLink(_driver) as db:
        print(db.update("UPDATE XF_STAFF SET XF_STAFFCODE = XF_STAFFCODE WHERE XF_STAFFCODE = %s", ("ADMIN",)))
        pass


if __name__ == '__main__':
    with open_link(ORACLE_DRIVER, "jdbc:oracle:thin:@172.31.2.100:1521:ORA100", "MD61_SMSC_1118",
                   "MD61_SMSC_1118") as db:
        print(db.query("select xf_password from xf_staff where xf_staffcode = 'ADMIN'"))
