import os
import threading
import handlers
import driver

RUN_TYPE = {
    'LOOP': 'loop',
    'ONCE': 'once',
    'NOT_SET': 'not_set',
    'PARALLEL': 'parallel'
}


def _apply_if(target, extra):
    for k, v in extra.items():
        if k not in target:
            target[k] = v


class Task(object):

    def __init__(self, task_config, data):
        if not task_config:
            return
        self._config = task_config

        if not data:
            data = {}
        self._data = data

        self._run_config = task_config.get('run', {})

        if self._run_config.get('times') and not self._run_config.get('type'):
            self._run_config['type'] = RUN_TYPE['LOOP']

        _apply_if(self._run_config, {
            'type': RUN_TYPE['NOT_SET'],
            'times': float('Inf')
        })

        run_type = self._run_config['type']
        if run_type == RUN_TYPE['ONCE']:
            self._run_config['times'] = 1
        elif run_type == RUN_TYPE['LOOP'] and not self._run_config.get('times'):
            self._run_config['times'] = float('Inf')

        self._run_times = 0

        self._driver = task_config.get('driver', None)

        self._name = task_config.get('name', '')
        if not self._name:
            self._name = task_config.get('opr', '')

        if not isinstance(self._driver, driver.Driver):
            self._init_driver()

        self._task = []
        self._init_task()

    def __del__(self):

        pass

    def _init_driver(self):
        if not self._config.get('driver'):
            return

        self._driver = driver.Driver(
            self._driver
        )
        self._driver.init()

    def _init_task(self):
        for task_config in self._config.get('task', []):

            if not task_config.get('driver'):
                task_config['driver'] = self._driver

            self._task.append(
                Task(task_config, self._data)
            )

    def run(self):
        run_config = self._run_config
        run_type = run_config['type']
        limit = run_config['times']

        if run_type == RUN_TYPE['NOT_SET']:
            self._run_once()
            return

        if self._run_times >= limit:
            return

        if run_type == RUN_TYPE['ONCE']:
            self._run_once()
            return

        if run_type == RUN_TYPE['LOOP']:
            while self._run_times < limit:
                self._run_once()

        if run_type == RUN_TYPE['PARALLEL']:
            self._parallel_run_once()

    def _run_once(self):
        self.run_opr()
        for task in self._task:
            task.run()
        self._run_times += 1

    # should use thread pool instead
    def _parallel_run_once(self):
        self.run_opr()

        for task in self._task:
            def get_task_fn(task):
                def task_fn():
                    print('threading %s' % threading.current_thread().ident)
                    task.run()
                return task_fn
            t = threading.Thread(target=get_task_fn(task))
            t.start()

        self._run_times += 1

    def run_opr(self):
        opr = self._config.get('opr', None)
        print('[%s] [%s] [%s]' % (self._name, self._driver, opr))

        if not opr:
            return

        if opr == 'py_script':
            return self.run_py_script()

        if opr == 'js_script':
            return self.run_js_script()

        fn = getattr(handlers, opr, handlers.empty_opr)
        fn(self)

    def run_py_script(self):
        module_path = os.path.basename(self._data['root']) + '.' + self._config.get('src')
        module = __import__(module_path, fromlist=self._config.get('src'))
        if hasattr(module, 'run'):
            module.run(self, self._data)

    def run_js_script(self):
        script = self._config.get('script')
        if not script:
            file = open(
                self._get_file_path(self._config.get('src')),
                'r',
                encoding='utf8'
            )
            script = file.read()
            file.close()
        self._driver.get_driver().execute_script(script)

    def get_config(self):
        return self._config

    def get_driver(self):
        return self._driver

    def get_name(self):
        return self._name

    def _get_file_path(self, file):
        return os.path.join(
            self._data.get('root'),
            file
        )
