import time
import re
from selenium import webdriver
import pid_finder


BROWSER_TYPE = {
    'Firefox': 'Firefox',
    'Chrome': 'Chrome',
    'Ie': 'Ie'
}


class Driver(object):
    def __init__(self, config):
        if config is True:
            config = {}

        self._config = config
        self._drivers = None
        self._pids = {}

    # def __del__(self):
    #     if self._drivers:
    #         self.quit()

    def init(self):
        self._init_drivers()

    def _init_drivers(self):
        browsers = self._config.get('browser') or [BROWSER_TYPE['Chrome']]
        if not isinstance(browsers, list):
            return

        self._drivers = []
        for browser_type in browsers:
            if browser_type not in BROWSER_TYPE:
                continue
            self._drivers.append({
                'type': browser_type,
                'driver': self._init_driver(browser_type)
            })

    def _init_driver(self, browser_type):
        print('init driver: %s' % browser_type)

        pids = pid_finder.get_all_pids(browser_type)

        driver_fn = getattr(webdriver, BROWSER_TYPE[browser_type])
        driver = driver_fn()
        url = self._config.get('default_url')
        if url:
            driver.get(url)

            if browser_type == BROWSER_TYPE['Ie']:
                self._skip_ie_https_warning(driver, url)

            sleep_time = float(self._config.get('sleep_time', -1))
            if sleep_time > 0:
                time.sleep(sleep_time)

        time.sleep(0.5)
        pids = pid_finder.get_all_pids(browser_type) - pids
        self._pids[browser_type] = pids

        return driver

    def _skip_ie_https_warning(self, driver, url):
        if not re.match('^https', url):
            return

        time.sleep(3)

        script = '''
            var linkDom = document.getElementById('overridelink');
            if (linkDom) {
                linkDom.click()
            }
        '''

        # 在https告警页面使用execute_script将产生脚本错误
        script = 'javascript:' + re.sub('\s+', ' ', script)
        driver.get(script)

        time.sleep(1)

    def get_pids(self, get_all_pid=False):
        pids = []
        url = self._config.get('default_url')

        def collect_pids(browser_type, driver):
            if get_all_pid:
                ret = list(
                    self._pids[BROWSER_TYPE[browser_type]]
                )

            elif browser_type == BROWSER_TYPE['Ie']:
                ret = list(
                    self._pids[BROWSER_TYPE[browser_type]]
                )
                ret = pid_finder.get_max_mem_pid(ret)

            else:
                ret = pid_finder.get_pids(driver, browser_type, {
                    'url': url
                })
                ret = pid_finder.get_max_mem_pid(ret)

            nonlocal pids
            ret = map(lambda pid: {
                'pid': pid,
                'name': browser_type
            }, ret)
            pids += ret

        self.execute(collect_pids)
        return pids

    def execute(self, cb):
        if not self._drivers:
            return

        for driver in self._drivers:
            cb(driver['type'], driver['driver'])

    def execute_script(self, script):
        ret = []

        def script_fn(broswer_type, driver):
            ret.append(
                driver.execute_script(script)
            )

        self.execute(script_fn)
        return ret[0] or ''

    def get(self, url):
        self.execute(
            lambda browser_type, driver: driver.get(url)
        )

    def quit(self):
        self.execute(
            lambda browser_type, driver: driver.quit()
        )
