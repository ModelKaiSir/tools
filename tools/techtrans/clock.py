# 科传二维码打卡
from tools.toolKit.web_driver_helper import Op
import tools.toolKit.web_driver_helper as helper
import time
import random


@helper.driver({Op.MOBILEEMULATION: {'deviceName': 'iPhone X'}, Op.DETACH: True})
def __clock_by_jiandanyun__(**kwargs):
    def wait_xpath(path):
        return helper.waiting_find_element_by_xpath(wait, path)

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
    wait_xpath("//*[@id='root']")

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

    wait_xpath(
        "//*[@id='root']//div[@class='field-label']/./div[contains(text(), '体温')]/../../div[@class='field-component']//div[@contenteditable='true']") \
        .send_keys(kwargs.get('c'))

    location_xpath('')
    # select_item_xpath('过去14天有否离开本市', '否')
    select_checkbox_xpath('身体状况', '自觉无症状')
    select_item_xpath('防控措施落实情况', '口罩每日一换，出入马上洗手并消毒')

    find_component_xpath('签名').click()
    pass


JIAN_DAO_YUN: str = "JIANDAOYUN"
__CLOKER = {JIAN_DAO_YUN: __clock_by_jiandanyun__}


def clock(tag):
    c = random.Random().choice([36.1, 36.5, 36.3, 36.7])
    __CLOKER[tag](url="https://u5tst0586o.jiandaoyun.com/f/5fba8255205782000652c48c", c=str(c))
