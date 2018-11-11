import time
import os
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains

# only for chrome 68!

pid_script = ''
support_auto_get_pid = True


def get_pid_script(script_path):
    global pid_script
    if pid_script:
        return pid_script

    file = open(script_path, 'r', encoding='utf-8')
    pid_script = file.read()
    file.close()
    return pid_script


def get_current_pids(driver):
    driver.execute_script(pid_script)
    time.sleep(0.5)
    return driver.execute_script(pid_script)


def open_new_tag(driver, url):
    # ActionChains(driver).key_down(Keys.CONTROL).send_keys('LMB')\
    #    .key_up(Keys.CONTROL).perform()
    driver.execute_script('window.open("' + url + '")')


def auto_get_pid(config, driver):
    url = config['url']
    driver.get('chrome://memory-internals')
    get_pid_script(
        os.path.join(os.path.dirname(__file__), './scripts/get_chrome_tab_pids.js')
    )
    get_current_pids(driver)
    init_handle = driver.current_window_handle
    time.sleep(1)
    pids_init = get_current_pids(driver)
    open_new_tag(driver, url)
    driver.switch_to.window(init_handle)

    pids_after_tab1 = get_current_pids(driver)

    target_pids = set(pids_after_tab1) - set(pids_init)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    if len(target_pids) == 1:
        pid = list(target_pids)[0]
        print('[%s] pid: %s'%(config['name'], pid))
        return pid

    print('[%s] auto find tag pid fail'%config['name'])
    print('[%s] %s -> %s'%(config['name'], pids_init, pids_after_tab1))


def get_pid(driver, config):
    global support_auto_get_pid
    if support_auto_get_pid:
        pid = auto_get_pid(config, driver)
        if not pid:
            support_auto_get_pid = False
        else:
            return pid
    pid = input('[%s] input pid: ' % config['name'])
    return int(pid)

