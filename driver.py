import time
from selenium import webdriver


class Driver(object):
    def __init__(self, config):
        if config is True:
            config = {}

        self._config = config
        self._driver = None

    # def __del__(self):
    #     if self._driver:
    #         self._driver.quit()

    def init(self):
        self._init_driver()
        self._get_pid()

    def _init_driver(self):
        print('init driver')
        self._driver = webdriver.Chrome()
        url = self._config.get('default_url')
        if url:
            self._driver.get(url)
            sleep_time = float(self._config.get('sleep_time', -1))
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _get_pid(self):
        print('get pid')

    def execute(self):
        pass

    def get_driver(self):
        return self._driver
