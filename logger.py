import time


class Logger(object):

    def __init__(self, config = {}):
        self._config = config
        self._debug = config.get('debug', False)
        self._name = config.get('name', 'logger')

    def log(self, msg):
        print('[%s] %s %s' % (self._name, self._get_time(), msg))

    def error(self, msg):
        print('[%s] %s error: %s' % (self._name, self._get_time(), msg))

    def debug(self, msg):
        if not self._debug:
            return

        print('[%s] %s %s' % (self._name, self._get_time(), msg))

    def _get_time(self):
        return time.strftime(
            '%Y-%m-%d %H:%M:%S',
            time.localtime(time.time())
        )


class EventLogger(Logger):

    def __init__(self, config = {}):

        super(EventLogger, self).__init__(config)
        self._events = []

    '''
    thread safe?
    '''
    def log_event(self, event = {}):
        self.debug(event)

        self._events.append({
            'time': self._get_time(),
            'name': event['name'],
            'event': event['event'],
            'msg': event['msg']
        })

    def log_debug_event(self, event):
        if not self._debug:
            return
        self.log_event(event)

    def get_events(self):
        return self._events

    # def __del__(self):
    #     self._events = None


class EmptyEventLogger(EventLogger):

    def log_event(self, event = {}):
        pass

    def debug_log_event(self, event):
        pass


empty_event_logger = EmptyEventLogger()



