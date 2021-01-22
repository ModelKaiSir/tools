# 科传二维码打卡
from tools.toolKit.web_driver_helper import Op
import tools.toolKit.web_driver_helper as helper
import time
import random


def wait_xpath(wait, xpath):
    return helper.waiting_find_element_by_xpath(wait, xpath)


@helper.driver({Op.MOBILEEMULATION: {'deviceName': 'iPhone X'}, Op.DETACH: True})
def __clock_by_jdy__(**kwargs):
    def find_component_xpath(_text):
        return wait_xpath(
            "//*[@id='root']//div[@class='field-label']/./div[contains(text(), '{text}')]/../../div[@class='field-component']".format(
                text=_text))

    def click_xpath(_text):
        _r = find_component_xpath(_text)
        _r.click()
        pass

    def search(_text):
        _r = wait_xpath("//*/input[@placeholder='搜索']")
        _r.send_keys(_text)

    def radio_item_xpath(_item):
        _r = wait_xpath("//span[@class='radio-text' and text()='{item}']".format(item=_item))
        # _r.click()
        _driver.execute_script("arguments[0].click();", _r)

    def button_click_xpath(_name):
        _r = wait_xpath("//div[contains(@class,'x-button')]/div[text()='{}']/..".format(_name))
        _driver.execute_script("arguments[0].click();", _r)

    def select_item_xpath(_text, _item):
        _r = wait_xpath(
            "//*[@id='root']//div[@class='field-label']/./div[contains(text(), '{text}')]/../../div[@class='field-component']//div[contains(@class,'group-item')]//span[text()='{item}']/..".format(
                text=_text, item=_item))
        _driver.execute_script("arguments[0].click();", _r)

    def select_checkbox_xpath(_text, _item):
        _r = wait_xpath(
            "//*[@id='root']//div[@class='field-label']/./div[contains(text(), '{text}')]/../../div[@class='field-component']//div[contains(@class,'group-item')]//span[text()='{item}']/../..".format(
                text=_text, item=_item))
        _r.click()

    def location_xpath(_text):
        _r = wait_xpath(
            "//*[@id='root']//div[@class='field-label']/./div[contains(text(),'{text}')]/../../div[@class='field-component']//div[@class='location-btn']".format(
                text=_text))
        _r.click()
        pass

    _driver = kwargs['driver']
    wait = kwargs['wait']
    wait_xpath(wait, "//*[@id='root']")

    click_xpath('区域/部门')
    search("研发部.华东组")
    radio_item_xpath('研发部.华东组')

    click_xpath('姓名')
    search("邱凯")
    radio_item_xpath('邱凯')

    click_xpath('填写时间')
    button_click_xpath('确定')
    time.sleep(1)
    select_item_xpath('工作地', '广州')
    select_item_xpath('情况', '回公司上班')

    wait_xpath(wait,
               "//*[@id='root']//div[@class='field-label']/./div[contains(text(), '体温')]/../../div[@class='field-component']//div[@contenteditable='true']") \
        .send_keys(kwargs.get('c'))

    location_xpath('')
    # select_item_xpath('过去14天有否离开本市', '否')
    select_checkbox_xpath('身体状况', '自觉无症状')
    select_item_xpath('防控措施落实情况', '口罩每日一换，出入马上洗手并消毒')

    find_component_xpath('签名').click()
    pass


#
# Op.MOBILEEMULATION: {'deviceName': 'iPhone X'},
@helper.driver({Op.DETACH: True})
def __clock_by_wjx__(**kwargs):
    def search(_text):
        _element = wait_xpath(wait, "//*/input[@type='search']")
        _element.click()
        _element.send_keys(_text)
        # select first item
        time.sleep(0.5)
        _element = wait_xpath(wait, "//*/span[@class='select2-results']//li[1]")
        _element.click()

    temperature = random.Random().choice([36.0 + (d * 0.1) for d in range(7)])

    wait = kwargs['wait']
    # loading success
    wait_xpath(wait, "//*[@id='form1']")
    # 部门
    element = wait_xpath(wait, "//*/div[contains(text(), '部门')]/../div[2]//span[@role = 'combobox']")
    element.click()
    # 研发部华东组
    search("华东组")

    # 姓名
    element = wait_xpath(wait, "//*/div[contains(text(), '姓名')]/../div[2]//input")
    element.send_keys(kwargs['name'])
    # 工作地
    element = wait_xpath(wait, "//*/div[contains(text(), '工作地')]/../div[2]//span[@role = 'combobox']")
    element.click()
    search("广州")
    # 今日情况
    element = wait_xpath(wait, "//*/div[contains(text(), '今日情况')]/../div[2]//span[@role = 'combobox']")
    element.click()
    element = wait_xpath(wait, "//*/li[contains(text(), '上班')]")
    element.click()
    # 当前体温
    element = wait_xpath(wait, "//*/div[contains(text(), '体温')]/../div[2]//input")
    element.send_keys(str(temperature))
    # 当前情况
    element = wait_xpath(wait,
                         "//*/div[contains(text(), '当前情况')]/..//div[@class='ui-checkbox']//div[contains(text(), '无症状')]")
    element.click()
    # 防控措施
    element = wait_xpath(wait, "//*/div[contains(text(), '防控措施')]/../div[2]//span[@role = 'combobox']")
    element.click()
    element = wait_xpath(wait, "//*/li[contains(text(), '口罩每日一换')]")
    element.click()
    # 填写日期
    # element = wait_xpath(wait, "//*/div[contains(text(), '填写日期')]/../div[2]//input")
    # element.click()
    # time.sleep(2)
    # element = wait_xpath(wait, "//*/a[text()='确定']")
    # element.click()

    # 当前位置
    element = wait_xpath(wait, "//*[@id='div8']/div[2]/label")
    element.click()
    pass


JIAN_DAO_YUN: str = "JIAN_DAO_YUN"
WJX: str = "WJX"

URL = {
    JIAN_DAO_YUN: "https://u5tst0586o.jiandaoyun.com/f/5fba8255205782000652c48c",
    WJX: "https://www.wjx.cn/m/99652985.aspx"
}

__CLOCK = {
    JIAN_DAO_YUN: __clock_by_jdy__,
    WJX: __clock_by_wjx__
}


def clock(**kwargs):
    """kwargs: clock = 打卡源, name = 打卡人, c = 体温"""
    c = random.Random().choice([36.1, 36.5, 36.3, 36.7])
    _clock = kwargs.get('clock')
    kwargs.update({"c": c})
    kwargs.update({"url": URL[_clock]})
    __CLOCK[_clock](**kwargs)
