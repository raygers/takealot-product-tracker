import logging
import json
import pendulum
import decimal
from typing import Dict, Any


# Used to encode data from DynamoDB where numbers are passed back as Decimal
class DecimalEncoder(json.JSONEncoder):
    # pylint: disable=E0202
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def create_logger(name: str):
    console_log_handler = logging.StreamHandler()
    console_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s'))

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(console_log_handler)

    return logger


def read_json_file(filename: str) -> Dict[str, Any]:
    with open(filename) as ifile:
        return json.load(ifile)


def generate_received_timestamp() -> str:
    return pendulum.now(tz='Africa/Johannesburg').to_datetime_string()


def convert_to_bool(value, default_value):
    if value is None:
        return default_value
    elif isinstance(value, str):
        value = value.lower()
        if value in ['true', 'yes', '1', 't', 'y']:
            return True
        elif value in ['false', 'no', '0', 'f', 'n']:
            return False
    elif isinstance(value, int):
        return value > 0
    
    raise Exception(f'cannot convert value to a boolean: {value}')


        