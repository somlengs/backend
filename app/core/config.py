import logging
import os
from typing import Literal, cast

from dotenv import load_dotenv

from app.entities.types import LogLevelT
from app.shared.utils import optional_env, require_env

load_dotenv()


class Config:
    LOG_LEVEL: LogLevelT = require_env('LOG_LEVEL', logging.getLevelName)
    ENVIRONMENT = cast(
        Literal['DEV', 'UAT', 'PROD'],
        os.getenv('ENV', 'DEV').upper(),
    )

    
    PORT = optional_env('PORT', 8080)

    class Supabase:
        PROJECT_NAME: str = require_env('SUPABASE_PROJECT_NAME')
        PROJECT_ID: str = require_env('SUPABASE_PROJECT_ID')
        DATABASE_PASSWORD: str = require_env('SUPABASE_PASSWORD')

    class Telegram:
        TOKEN = optional_env('TELEGRAM_TOKEN', '')
        CHAT_ID = optional_env('TELEGRAM_CHAT_ID', '')
