from typing import Literal

import logging

type LogLevelT = int | Literal[
    'CRITICAL',
    'FATAL',
    'ERROR',
    'WARNING',
    'WARN',
    'INFO',
    'DEBUG',
    'NOTSET',
]
