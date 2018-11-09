def run(task, data):
    pages = task.run_js_script(file='js/get_pages.js')
    if not pages:
        return
