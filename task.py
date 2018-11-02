import os
import threading
import handlers
import driver
import logger
import process_logger

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

        self._threads = []

        self._driver = task_config.get('driver', None)

        self._name = task_config.get('name', '')
        if not self._name:
            self._name = task_config.get('opr', '')

        self._init_process_logger()

        self._logger = self._config.get('logger', logger.empty_event_logger)
        if self._logger and not isinstance(self._logger, logger.Logger):
            if not isinstance(self._logger, dict):
                self._logger = {}
            self._logger = logger.EventLogger({
                'name': self._logger.get('name', self._name),
                'debug': self._logger.get('debug', False)
            })

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
        self._on_driver_init()

    def _on_driver_init(self):

        if self._process_logger and \
                self._process_logger.get_config()\
                        .get('log_driver') is not False:
            pid = self._driver.get_pid()
            self._logger.debug('get page pid: %s' % pid)
            if not isinstance(pid, int):
                return
            self._process_logger.add({
                'name': self._name,
                'pid': pid
            })

    def _init_process_logger(self):
        config = self._config.get('process_logger')
        if not config:
            return

        if isinstance(config, process_logger.ProcessLogger):
            self._process_logger = config
            return

        self._process_logger = process_logger.ProcessLogger(config)

    def _init_task(self):
        for task_config in self._config.get('task', []):

            if not task_config.get('driver'):
                task_config['driver'] = self._driver

            if not task_config.get('logger'):
                task_config['logger'] = self._logger

            if not task_config.get('process_logger'):
                task_config['process_logger'] = self._process_logger

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
                    # print('threading %s' % threading.current_thread().ident)
                    self._logger.debug('thread id: %s' % threading.current_thread().ident)
                    task.run()
                return task_fn
            t = threading.Thread(target=get_task_fn(task))
            self._threads.append(t)
            t.start()

        self._run_times += 1
        for t in self._threads:
            t.join()
        self._on_parallel_task_end()

    def _on_parallel_task_end(self):
        # task_end_fn = self._config.get('task_end_fn')
        # if not task_end_fn:
        #     return

        self._logger.log('parallel task end')
        # task_end_fn()
        self._threads = []

    def log_event(self, event, msg):
        self._logger.log_event({
            'name': self._name,
            'event': event,
            'msg': msg
        })

    def run_opr(self):
        opr = self._config.get('opr', None)
        # print('[%s] [%s] [%s]' % (self._name, self._driver, opr))

        if not opr:
            return

        self._logger.debug('[%s] [%s] [%s]' % (self._name, self._driver, opr))

        if opr == 'py_script':
            self.log_event('pyscript', 'run %s' % self._config.get('src'))
            return self.run_py_script()

        if opr == 'js_script':
            self.log_event('pyscript', 'run %s' % self._config.get('src'))
            return self.run_js_script()

        msg = ''
        fn = getattr(handlers, opr, handlers.empty_opr)
        formatter = getattr(handlers, opr + '_formatter', None)
        if formatter:
            msg = formatter(self)
        self.log_event(opr, msg)
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

    def get_logger(self):
        return self._logger

    def get_process_logger(self):
        return self._process_logger

    def _get_file_path(self, file):
        return os.path.join(
            self._data.get('root'),
            file
        )
