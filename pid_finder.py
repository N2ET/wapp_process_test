import time
import os
import psutil

from process_logger import ProcessLogger
process_logger = ProcessLogger()

scripts = {

}


def get_pid_script(browser_type, script_path):
    if scripts.get(browser_type):
        return scripts[browser_type]

    script_path = os.path.join(os.path.dirname(__file__), script_path)
    file = open(script_path, 'r', encoding='utf-8')
    pid_script = file.read()
    file.close()

    scripts[browser_type] = pid_script
    return pid_script


def get_chrome_current_pids(driver):
    pid_script = get_pid_script(
        'Chrome',
        './scripts/get_chrome_tab_pids.js'
    )
    driver.execute_script(pid_script)
    time.sleep(0.5)
    return driver.execute_script(pid_script)


def open_new_tag(driver, url):
    driver.execute_script('window.open("' + url + '")')


def get_pids(driver, browser_type, config):
    pids = []
    if browser_type == 'Chrome':
        pids = get_chrome_pids(driver, config)
    elif browser_type == 'Firefox':
        pids = get_firefox_pids(driver, config)
    elif browser_type == 'Ie':
        pids = get_ie_pids(driver, config)

    return pids


def get_chrome_pids(driver, config):
    url = config['url']
    driver.get(url)
    open_new_tag(driver, 'about:blank')
    driver.switch_to.window(driver.window_handles[1])
    driver.get('chrome://memory-internals')

    time.sleep(1)
    pids = get_chrome_current_pids(driver)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return pids


def get_firefox_pids(driver, config):
    url = config['url']
    driver.get(url)

    # 不能通过脚本打开
    open_new_tag(driver, 'about:blank')
    driver.switch_to.window(driver.window_handles[1])
    driver.get('about:memory')

    time.sleep(3)
    driver.execute_script('''
        var dom = document.getElementById('measureButton');
        if (dom) {
            dom.click();
        }
    ''')

    time.sleep(1)

    # 通过url查找进程id，不包括浏览器主进程id
    script = get_pid_script(
        'Firefox',
        os.path.join(os.path.dirname(__file__), './scripts/get_firefox_tab_pids.js')
    ) + ('return getPids("%s");' % url)

    pids = driver.execute_script(script)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return pids


def get_ie_pids(driver, config):
    return []


def get_all_pids(browser_type):
    name = {
        'Firefox': 'firefox.exe',
        'Chrome': 'chrome.exe',
        'Ie': 'iexplore.exe'
    }[browser_type]
    pids = psutil.pids()
    ret = set()
    for pid in pids:
        try:
            p = psutil.Process(pid)
            if p.name() == name:
                ret.add(pid)
        except Exception:
            pass

    return ret


def get_max_mem_pid(pids):
    if len(pids) == 1:
        return pids

    max_mem = 0
    max_pid = 0

    ret = []

    for pid in pids:
        info = process_logger.get_process_stat(pid)
        if not info:
            continue
        if max_mem < info['mem'].private:
            max_mem = info['mem'].private
            max_pid = pid

    if max_pid:
        return [max_pid]
    else:
        return ret
