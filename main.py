import yaml
import os
from task import Task


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


t = Task(
    setting.get('task')[0],
    setting.get('global')
)

print(t)

t.run()

print(t)
