import time
from selenium import webdriver
import pid_finder


class Driver(object):
    def __init__(self, config):
        if config is True:
            config = {}

        self._config = config
        self._driver = None
        self._pid = None

    # def __del__(self):
    #     if self._driver:
    #         self._driver.quit()

    def init(self):
        self._init_driver()

    def _init_driver(self):
        print('init driver')
        self._driver = webdriver.Chrome()
        url = self._config.get('default_url')
        if url:
            self._driver.get(url)
            sleep_time = float(self._config.get('sleep_time', -1))
            if sleep_time > 0:
                time.sleep(sleep_time)

    def get_pid(self):
        url = self._config['default_url']
        self._pid = pid_finder.get_pid(self._driver, {
            'url': url,
            'name': url
        })
        return self._pid

    def execute(self):
        pass

    def get_driver(self):
        return self._driver
