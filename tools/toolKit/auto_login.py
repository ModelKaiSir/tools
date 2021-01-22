import functools
import web_driver_helper as helper
import sys

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

XPATH_USER = '//input[@type="text" and @class="v-filterselect-input"]'
XPATH_PASSWORD = '//input[@type="password"]'
XPATH_LOGIN_BTN = '//*[@id="okbtn"]'
ADMIN_USER = "ADMIN"
QUERY_USER_PASSWORD = "SELECT XF_PASSWORD FROM XF_STAFF WHERE XF_STAFFCODE = :staffcode"
QUERY_USER_PASSWORD_SQL_SERVER = "SELECT XF_PASSWORD FROM XF_STAFF WHERE XF_STAFFCODE = %s"

ORACLE_DRIVER = "oracle.jdbc.driver.OracleDriver"
SQL_SERVER_DRIVER = "com.microsoft.sqlserver.jdbc.SQLServerDriver"

URL_POS61 = "http://localhost:8080/POS61"
URL_POS65 = "http://localhost:8080/POS65"
URL_POS65RD = "http://localhost:8080/POS65RD"
URL_POS65YTC = "http://localhost:8080/POS65YTC"

ORACLE = "oracle"
SQL_SERVER = "sqlserver"

def query_password(user):
    pass
    # def _query(_r):
    #
    #     if _r is None or len(_r) <= 0:
    #         return None
    #     else:
    #         return _r[0]
    #
    # if QUERY.is_oracle():
    #     with OracleConnectionManager(QUERY.connection()) as m:
    #
    #         _r = m.query(QUERY_USER_PASSWORD, {"staffcode": user})
    #         return _query(_r)
    #         pass
    # elif QUERY.is_sql_server():
    #     with SqlServerConnectionManager(QUERY.connection()) as m:
    #
    #         _r = m.query(QUERY_USER_PASSWORD_SQL_SERVER, (user,))
    #         return _query(_r)
    #         pass


def auto_login(**kwargs):
    password = query_password(kwargs.get('user'))
    print('password = ', password)
    # 获取元素, wait for load success
    input_user = helper.waiting_find_element_by_xpath(kwargs['wait'], XPATH_USER)

    # 双击全选
    ActionChains(kwargs['driver']).double_click(input_user).perform()

    # put user
    input_user.send_keys(kwargs.get('user'))
    input_user.send_keys(Keys.ENTER)
    input_user.send_keys(Keys.ENTER)

    # put password
    input_password = kwargs['driver'].find_element_by_xpath(XPATH_PASSWORD)
    input_password.clear()
    input_password.send_keys(password)
    input_password.send_keys(Keys.ENTER)

    # login
    login = kwargs['driver'].find_element_by_xpath(XPATH_LOGIN_BTN)
    login.click()


def open_menu(wait):
    item = helper.waiting_find_element_by_xpath(wait, "//div[text()='财务管理']")
    item.click()
    item = helper.waiting_find_element_by_xpath(wait, "//span[text()='合同退租清算管理']")
    item.click()
    item = helper.waiting_find_element_by_xpath(wait, "//span[text()='退租清算维护']")
    item.click()


def click_menu(wait, name):
    item = helper.waiting_find_element_by_xpath(wait, "//span[contains(text(), '{}')][1]".format(name))
    item.click()


def search(**kwargs):
    if kwargs.get('content') is None:
        return

    item = helper.waiting_find_element_by_xpath(kwargs['wait'], "//div[contains(@class, 'menuTree_SearchField')]/input")

    ActionChains(kwargs['driver']).double_click(item).perform()
    item.send_keys(kwargs.get('content'))
    click_menu(kwargs['wait'], kwargs.get('content'))
    pass


def sqlserver(db, url):
    def decorator(fn):
        @functools.wraps(fn)
        def warpper(**kwargs):
            driver = SQL_SERVER_DRIVER
            connection_url = "jdbc:sqlserver://172.31.2.100:1433;DatabaseName={};".format(db)
            global QUERY
            QUERY = QUERY.driver(driver).url(connection_url).db_user("SA").pwd("ORA100")

            kwargs.update({"url": url})
            return fn(**kwargs)
            pass

        return warpper
        pass

    return decorator
    pass


def oracle(db_user, pwd, url, connection_url="jdbc:oracle:thin:@172.31.2.100:1521:ORA100"):
    def decorator(fn):
        @functools.wraps(fn)
        def warpper(**kwargs):
            driver = ORACLE_DRIVER
            global QUERY
            QUERY = QUERY.driver(driver).url(connection_url).db_user(db_user).pwd(pwd)

            kwargs.update({"url": url})
            return fn(**kwargs)
            pass

        return warpper
        pass

    return decorator
    pass


def start(**kwargs):
    if kwargs.get('type') == 'oracle':

        # connection_url="jdbc:oracle:thin:@172.31.1.155:1521:ORA155"
        @oracle(kwargs.get('db'), kwargs.get('db'), kwargs.get('url'))
        @helper.driver({helper.Op.DEBUGGERADDRESS: "127.0.0.1:9222"})
        def fn(**kk):
            user = kk.get('user')
            _driver = kk.get('driver')
            _wait = kk.get('wait')
            auto_login(wait=_wait, driver=_driver, user=user)
            search(wait=_wait, driver=_driver, content=kwargs.get('search'))
            pass

        return fn(**kwargs)
    elif kwargs.get('type') == 'sqlserver':

        @sqlserver(kwargs.get('db'),
                   kwargs.get('url'))  # connection_url="jdbc:oracle:thin:@172.31.1.155:1521:ORA155"
        @helper.driver({helper.Op.DEBUGGERADDRESS: "127.0.0.1:9222"})
        def fn(**kk):
            user = kk.get('user')
            _driver = kk.get('driver')
            _wait = kk.get('wait')
            auto_login(wait=_wait, driver=_driver, user=user)
            search(wait=_wait, driver=_driver, content=kwargs.get('search'))
            pass

        return fn(**kwargs)


# chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\admin\selenium\AutomationProfile"
# search='游戏币获取设置',

cache = {

    "MD61_SMSC_1118": [ADMIN_USER, URL_POS61, ORACLE, None, False],
    "MD61_5050": [ADMIN_USER, URL_POS61, SQL_SERVER, "意向合同维护", False],
    "MD61_SJH1": [ADMIN_USER, URL_POS61, SQL_SERVER, None, False],
    "E65UTF8_RD": [ADMIN_USER, URL_POS65RD, ORACLE, None, False],
    "MD65_RUNDA": [ADMIN_USER, URL_POS65RD, ORACLE, None, False],
    "MD61_RAXH2": [ADMIN_USER, URL_POS61, ORACLE, None, False],
    "MD61_CJ": [ADMIN_USER, URL_POS61, SQL_SERVER, None, False]
}

if __name__ == '__main__':
    pass
