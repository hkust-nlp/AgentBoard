import bisect
import hashlib
import logging
import random
from os.path import dirname, abspath, join

PROJECT_DIR = dirname(dirname(dirname(abspath(__file__))))
HEADER_PATH = "../../data/webshop"
DATA_DIR = join(PROJECT_DIR, HEADER_PATH)
BASE_DIR = dirname(abspath(__file__))
DEBUG_PROD_SIZE = None  # set to `None` to disable

#DEFAULT_ATTR_PATH = join(DATA_DIR, '../data/items_ins_v2_1000.json')
#DEFAULT_FILE_PATH = join(DATA_DIR, '../data/items_shuffle_1000.json')
GOAL_PATH = join(DATA_DIR, 'test.jsonl')
DEFAULT_ATTR_PATH = join(DATA_DIR, 'data/items_ins_v2.json')
DEFAULT_FILE_PATH = join(DATA_DIR, 'data/items_shuffle.json')
DEFAULT_FILE_PATH = abspath(DEFAULT_FILE_PATH)
print(DEFAULT_FILE_PATH)

HUMAN_ATTR_PATH = join(DATA_DIR, 'data/items_human_ins.json')

def random_idx(cum_weights):
    """Generate random index by sampling uniformly from sum of all weights, then
    selecting the `min` between the position to keep the list sorted (via bisect)
    and the value of the second to last index
    """
    pos = random.uniform(0, cum_weights[-1])
    idx = bisect.bisect(cum_weights, pos)
    idx = min(idx, len(cum_weights) - 2)
    return idx

def setup_logger(session_id, user_log_dir):
    """Creates a log file and logging object for the corresponding session ID"""
    logger = logging.getLogger(session_id)
    formatter = logging.Formatter('%(message)s')
    file_handler = logging.FileHandler(
        user_log_dir / f'{session_id}.jsonl',
        mode='w',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger

def setup_subreward_logger(session_id, subreward_log_dir):
    """Creates a log file and logging object for the corresponding session ID"""
    logger = logging.getLogger('subreward_logger')
    formatter = logging.Formatter('%(message)s')
    file_handler = logging.FileHandler(
        subreward_log_dir / f'{session_id}.log',
        mode='w'
    )
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger

def generate_mturk_code(session_id: str) -> str:
    """Generates a redeem code corresponding to the session ID for an MTurk
    worker once the session is completed
    """
    sha = hashlib.sha1(session_id.encode())
    return sha.hexdigest()[:10].upper()
