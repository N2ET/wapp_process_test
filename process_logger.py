import time
import os
import threading
import json
import psutil
import util
from logger import Logger


class ProcessLogger(Logger):

    def __init__(self, config={}):
        self._config = config

        util.apply_if(self._config, {
            'interval': 1,
            'pre_interval': 0,
            'end_interval': 0,
            'output_dir': '',
            'filename': 'process_logger_log'
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

    def _collect(self):
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
                data[key]['time'].append(time.time())
                data[key]['value'].append({
                    "private": mem.private,
                    "rss": mem.rss,
                    "peak_wset": mem.peak_wset
                })
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
        pre_interval = self._config['pre_interval']
        if isinstance(pre_interval, (int, float)):
            self.log('wait %s sec(s) to start' % pre_interval)
            self.start(pre_interval)

    def pause(self):
        self._timer.cancel()
        self._timer = None

    def stop(self, delay_time=None):
        if not self._timer:
            return

        if not isinstance(delay_time, (int, float)):
            self.pause()
        else:
            self._timer = threading.Timer(
                delay_time,
                self.pause
            )
            self._timer.start()

    def delay_stop(self):
        end_interval = self._config['end_interval']
        if isinstance(end_interval, (int, float)):
            self.log('wait %s sec(s) to stop' % end_interval)
            self.stop(end_interval)

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
            os.makedirs(output_dir)

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






