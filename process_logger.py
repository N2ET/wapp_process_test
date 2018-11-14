import time
import os
import threading
import json
import psutil
import util
from logger import EventLogger


class ProcessLogger(EventLogger):

    def __init__(self, config={}):
        self._config = config

        util.apply_if(self._config, {
            'interval': 1,
            'start_interval': 0,
            'end_interval': 0,
            'output_dir': '',
            'filename': 'data'
        })

        super(ProcessLogger, self).__init__(self._config)

        self._debug = self._config.get('debug', False)
        self._name = self._config.get('name', 'process_logger')

        self._data = {}
        self._process = []
        self._timer = None

    def _run(self):
        self._collect()
        self._timer = threading.Timer(
            self._config['interval'],
            self._run
        )
        self._timer.start()

    def _collect(self, extra_data=None):
        data = self._data

        for p in self._process:
            try:
                stat = psutil.Process(p['pid'])
            except Exception as e:
                self.log(e)
                continue

            mem = stat.memory_info()
            self.log("%d(%s): %d Mb" % (p['pid'], p['name'], mem.private / 1024 / 1024))
            key = p['name']
            if data.get(key):
                value = {
                    "private": mem.private,
                    "rss": mem.rss,
                    "peak_wset": mem.peak_wset
                }

                if extra_data:
                    value['data'] = extra_data

                data[key]['time'].append(time.time())
                data[key]['value'].append(value)
            else:
                data[key] = p.copy()
                data[key]['time'] = []
                data[key]['value'] = []

    def start(self, delay_time=None):
        if self._timer:
            return

        if not isinstance(delay_time, (int, float)):
            self._run()
        else:
            self._timer = threading.Timer(
                delay_time,
                self._run
            )
            self._timer.start()

    def delay_start(self):
        pre_interval = self._config['start_interval']
        if isinstance(pre_interval, (int, float)):
            self.log('wait %s sec(s) to start' % pre_interval)
            self.start(pre_interval)
        self.start()

    def pause(self):
        self._timer.cancel()
        self._timer = None

    def stop(self, delay_time=None):
        if not self._timer:
            return

        if not isinstance(delay_time, (int, float)):
            self.pause()
        else:
            timer = threading.Timer(
                delay_time,
                self.pause
            )
            timer.start()
            return timer

    def delay_stop(self):
        end_interval = self._config['end_interval']
        if isinstance(end_interval, (int, float)):
            self.log('wait %s sec(s) to stop' % end_interval)
            timer = self.stop(end_interval)
            if timer:
                timer.join()

        self.stop()

    def _get_platform_info(self):
        return {
            'os': '',
            'cpu': '',
            'memory': ''
        }

    def save(self):
        output_dir = self._config['output_dir']
        filename = self._config['filename']
        js_filename = os.path.join(output_dir, filename + '.js')
        json_filename = os.path.join(output_dir, filename + '.json')

        data = {}

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                self.error(e)
                return

        if os.path.exists(json_filename):
            data = self._load_json(json_filename)

        key = self._get_time()
        data[key] = {
            'platform_info': self._get_platform_info(),
            'data': self._data
        }
        data = json.dumps(data, indent=4)

        self._write_file(
            json_filename,
            data
        )

        self._write_file(
            js_filename,
            'var jsonData = ' + data
        )

        self.log('done, write file %s, %s' % (js_filename, json_filename))

    def _load_json(self, filename):
        try:
            file = open(filename, 'r', encoding='utf8')
            data = json.load(file)
            file.close()
        except Exception:
            self.debug('last json file not exist, file %s' % filename)
            data = {}
        return data

    def _write_file(self, filename, data):
        try:
            file = open(filename, 'w', encoding='utf8')
            file.write(data)
            file.close()
        except Exception as e:
            self.error('write file failed, file: %s, %s' % (filename, e))

    def add(self, process):
        if isinstance(process, list):
            self._process += process

        if isinstance(process, dict):
            self._process.append(process)

    def remove(self, process):
        pass

    def get_config(self):
        return self._config

    def get_process_stat(self, pid):
        ret = {}
        try:
            stat = psutil.Process(pid)
            ret['mem'] = stat.memory_info()
            return ret
        except Exception:
            pass

    def log_event(self, event={}):
        super(ProcessLogger, self).log_event(event)
        self._collect(event)
