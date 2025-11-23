from typing import Literal


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
