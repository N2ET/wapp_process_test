import yaml
import os
from task import Task
import time

def load_config(config_path):
    file = open(config_path, 'r', encoding='utf-8')
    config = yaml.load(file)
    file.close()
    return config

dir = os.path.dirname(
    __file__
)
setting = load_config(
    os.path.join(
        os.path.normpath(dir),
        os.path.normcase('wapp/setting.yml')
    )
)
print(setting)

setting['global']['root'] = os.path.join(
    os.path.dirname(__file__),
    'wapp'
)

# t = Task(
#     setting.get('login'),
#     setting.get('global')
# )


# t = Task(
#     setting.get('task')[0],
#     setting.get('global')
# )

process_logger_config = setting.get('task')[0].get('process_logger')
if process_logger_config and not process_logger_config.get('output_dir'):
    process_logger_config['output_dir'] = os.path.join(dir, 'test')

t = Task(
    setting.get('task')[0],
    setting.get('global')
)

print(t)

t.get_process_logger().start()

t.run()

t.get_process_logger().delay_stop()
t.get_process_logger().save()

print(
    'main end :' +
    time.strftime(
        '%Y-%m-%d %H:%M:%S',
        time.localtime(time.time())
    )
)
