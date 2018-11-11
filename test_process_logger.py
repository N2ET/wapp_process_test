import time
import os
from process_logger import ProcessLogger

logger = ProcessLogger({
    'interval': 1,
    'output_dir': os.path.dirname(__file__) + '/test',
    'filename': 'test_log',
    'pre_interval': 1,
    'end_interval': 1
})

logger.delay_start()
logger.add([{
    'name': '111',
    'pid': 2460
}])
time.sleep(10)
logger.stop()
logger.save()
time.sleep(3)