import copy


def run(task, data):
    pages = task.run_js_script(file='js/get_pages.js')
    if not pages:
        return

    page_tasks = []
    task_config = data['global']['task_config']
    for page in pages:
        config = copy.deepcopy(task_config)
        config['name'] = page['name']
        for opr_task in config['task']:
            if opr_task.get('url') == '__task_url__':
                opr_task['url'] = page['url']
        page_tasks.append(config)
    data['task'][0]['task'] = page_tasks
    task.get_driver().quit()
