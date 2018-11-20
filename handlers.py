import time


def navigate_to(task):
    driver = task.get_driver()
    config = task.get_config()
    driver.execute(
        lambda browser_type, dr: dr.get(
            config.get('url')
        )
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
    driver = task.get_driver()
    config = task.get_config()

    def _do_click(browser_type, dr):
        dom = dr.find_element_by_css_selector(
            config.get('target_selector')
        )
        dom.click()

    try:
        driver.execute(_do_click)
    except Exception as e:
        task.get_logger().error('opr click error, %s' % e)


def click_formatter(task):
    config = task.get_config()
    return 'click %s' % config.get('target_selector')


def start_process_logger(task):
    logger = task.get_process_logger()
    logger.start()


def start_process_logger_formatter(task):
    return 'start process_logger'


def reload(task):
    driver = task.get_driver()
    driver.execute(lambda browser_type, dr: dr.execute_script('location.reload();'))


def reload_formatter(task):
    return 'reload'


def empty_opr(task):
    config = task.get_config()
    print('no such handler %s' % config.get('opr'))