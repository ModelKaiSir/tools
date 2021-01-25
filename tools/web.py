import functools
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

MOBILE_EMULATION = "mobileEmulation"
DEBUGGER_ADDRESS = "debuggerAddress"
DETACH = "detach"


def waiting_find_element_by_xpath(wait, path):
    return wait.until(EC.presence_of_element_located((By.XPATH, path)))
    pass


def driver(options):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(**kwargs):

            url = kwargs['url']
            time_out = kwargs.get('timeout') if kwargs.get('timeout') is not None else 20
            chrome_options = Options()
            if options is not None:
                for k, v in options.items():
                    chrome_options.add_experimental_option(k, v)

            new_window = bool(kwargs.get('new_window'))

            # 去掉webDriver属性，防止被识别为Selenium自动化操作
            option = webdriver.ChromeOptions()
            option.add_experimental_option('excludeSwitches', ['enable-automation'])
            option.add_experimental_option('useAutomationExtension', False)

            _driver = webdriver.Chrome(options=option, chrome_options=chrome_options)
            _driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })

            _driver.get(url)
            _driver.maximize_window()

            if new_window:
                # 打开新页面
                _driver.execute_script('window.open("{}")'.format(url))
                _driver.switch_to.window(_driver.window_handles[-1])
            pass

            kwargs.update({"driver": _driver, "wait": WebDriverWait(_driver, time_out)})
            return fn(**kwargs)
            pass

        return wrapper
        pass

    return decorator
