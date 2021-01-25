import functools
import sys

from tools import web
from tools import db_link
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

ORACLE = "oracle"
SQL_SERVER = "sqlserver"


@web.driver({web.DEBUGGER_ADDRESS: "127.0.0.1:9222"})
def login(**kwargs):
    # 获取元素, wait for load success
    input_user = web.waiting_find_element_by_xpath(kwargs['wait'], XPATH_USER)

    # 双击全选
    ActionChains(kwargs['driver']).double_click(input_user).perform()

    # 获取数据库连接
    with db_link.open_link(kwargs["db_driver"], kwargs["connection_url"], kwargs["user"], kwargs["pwd"]) as db:
        if kwargs["db_driver"] == ORACLE_DRIVER:
            password = db.query(QUERY_USER_PASSWORD, (ADMIN_USER,))
        else:
            password = db.query(QUERY_USER_PASSWORD_SQL_SERVER, (ADMIN_USER,))
            pass

        if password is not None and len(password) > 0:
            password = password[0][0]
            pass
        # put user
        input_user.send_keys(ADMIN_USER)
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
    item = web.waiting_find_element_by_xpath(wait, "//div[text()='财务管理']")
    item.click()
    item = web.waiting_find_element_by_xpath(wait, "//span[text()='合同退租清算管理']")
    item.click()
    item = web.waiting_find_element_by_xpath(wait, "//span[text()='退租清算维护']")
    item.click()


def click_menu(wait, name):
    item = web.waiting_find_element_by_xpath(wait, "//span[contains(text(), '{}')][1]".format(name))
    item.click()


def search(**kwargs):
    if kwargs.get('content') is None:
        return

    item = web.waiting_find_element_by_xpath(kwargs['wait'], "//div[contains(@class, 'menuTree_SearchField')]/input")

    ActionChains(kwargs['driver']).double_click(item).perform()
    item.send_keys(kwargs.get('content'))
    click_menu(kwargs['wait'], kwargs.get('content'))
    pass


if __name__ == '__main__':
    login(url="http://localhost:8080/POS61/", db_driver="com.microsoft.sqlserver.jdbc.SQLServerDriver",
          connection_url="jdbc:sqlserver://172.31.2.100:1433;DatabaseName=MD61_5058;", user="SA", pwd="ORA100")
