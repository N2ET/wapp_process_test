import time


def navigate_to(task):
    driver = task.get_driver().get_driver()
    config = task.get_config()
    driver.get(
        config.get('url')
    )


def navigate_to_formatter(task):
    config = task.get_config()
    return 'navigate to %s ' % config.get('url')


def sleep(task):
    sec = float(task.get_config().get('time'))
    if sec <= 0:
        return

    time.sleep(sec)


def sleep_formatter(task):
    config = task.get_config()
    return 'sleep %s' % config.get('time')


def click(task):
    driver = task.get_driver().get_driver()
    config = task.get_config()
    dom = driver.find_element_by_css_selector(
        config.get('target_selector')
    )
    dom.click()


def click_formatter(task):
    config = task.get_config()
    return 'click %s' % config.get('target_selector')


def empty_opr(task):
    config = task.get_config()
    print('no such handler %s' % config.get('opr'))