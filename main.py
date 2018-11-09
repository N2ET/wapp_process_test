import yaml
import os
from task import Task
import getopt
import sys


def load_config(config_path):
    try:
        file = open(config_path, 'r', encoding='utf-8')
        config = yaml.load(file)
        file.close()
    except Exception as e:
        print('load setting file failed, %s' % e)
        return None

    return config


def main(args):
    try:
        opts, arg = getopt.getopt(
            args,
            'f:',
            ['file=']
        )
    except getopt.GetoptError as e:
        print('argv error, %s ' % e)
        return

    file = None

    for k, v in opts:
        if k == '-f':
            file = v

    if not file:
        print('args -f missing')
        return

    if not os.path.isabs(file):
        file = os.path.join(
            os.path.dirname(__file__),
            file
        )
        file = os.path.normpath(file)
    setting_root = os.path.dirname(file)

    if not os.path.exists(file):
        print('setting file not exists')
        return

    setting = load_config(file)
    if not setting:
        return

    print('load setting file, %s' % file)

    setting['global']['root'] = setting_root

    if setting.get('pre'):
        setting['root'] = setting_root
        pre = Task(
            setting['pre'],
            setting
        )
        pre.run()

    if not setting.get('task'):
        return

    t = Task(
        setting('task')[0],
        setting.get('global')
    )
    process_logger = t.get_process_logger()
    process_logger.start()
    t.run()
    process_logger.delay_stop()
    process_logger.save()


# python main.py -f ./wapp/setting-1.yml
if __name__ == '__main__':
    main(sys.argv[1:])
