import yaml
import os
from task import Task
import getopt
import sys
import json


def load_config(config_path):
    try:
        file = open(config_path, 'r', encoding='utf-8')
        config = yaml.load(file)
        file.close()
    except Exception as e:
        print('load setting file failed, %s' % e)
        return None

    return config


def save_config(config_path, config):
    if os.path.exists(config_path):
        print('setting file exists, %s' % config_path)
    try:
        file = open(config_path, 'w', encoding='utf-8')
        yaml.dump(config, file, default_flow_style=False)
        file.close()
    except Exception as e:
        print(e)


def main(args):
    try:
        opts, arg = getopt.getopt(
            args,
            'psdf:',
            ['pre, save-setting-file, direct, file=']
        )
    except getopt.GetoptError as e:
        print('argv error, %s ' % e)
        return

    file = None
    save_setting_file = False
    skip_pre_task = False
    only_pre_task = False

    for k, v in opts:
        if k == '-f':
            file = v
        if k == '-s':
            save_setting_file = True
        if k == '-d':
            skip_pre_task = True
        if k == '-p':
            only_pre_task = True

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

    setting = json.loads(
        json.dumps(setting)
    )

    setting['global']['root'] = setting_root

    if setting.get('pre') and not skip_pre_task:
        setting['root'] = setting_root
        pre = Task(
            setting['pre'],
            setting
        )
        pre.run()
        del setting['pre']
        if save_setting_file:
            save_config(
                file + '.save.yml',
                setting
            )

    if only_pre_task:
        return

    if skip_pre_task:
        print('skip pre task')

    if not setting.get('task'):
        print('no task setting')
        return

    process_logger_config = setting.get('task')[0].get('process_logger')
    if process_logger_config and not process_logger_config.get('output_dir'):
        process_logger_config['output_dir'] = os.path.join(setting_root, 'process_logger')

    t = Task(
        setting['task'][0],
        setting.get('global')
    )

    process_logger = t.get_process_logger()
    if process_logger:
        process_logger.delay_start()
    t.run()
    if process_logger:
        process_logger.delay_stop()
        process_logger.save()


if __name__ == '__main__':
    main(sys.argv[1:])
