import logging
import os
import json
from pathlib import Path
from typing import Literal, cast

from dotenv import load_dotenv

from app.entities.types.other import LogLevelT
from app.shared.utils.other import optional_env, parse_list, require_env

load_dotenv()


class Config:
    LOG_LEVEL: LogLevelT = require_env('LOG_LEVEL', logging.getLevelName)
    ENVIRONMENT = cast(
        Literal['DEV', 'UAT', 'PROD'],
        os.getenv('ENV', 'DEV').upper(),
    )

    PORT = optional_env('PORT', 8080)

    CORS_ORIGINS = parse_list(require_env('CORS_ORIGINS'))
    ASR_URL = require_env('ASR_SERVICE_URL')
    CHAR_ENCODING = optional_env('CHAR_ENCODING', 'utf-8')
    MAX_TASKS_PER_PROJECT = optional_env('MAX_TASKS_PER_PROJECT', default=4)
    ASR_TIMEOUT = optional_env('ASR_TIMEOUT', default=120.0)

    PEM_KEY: bytes
    JWT_SECRET=require_env('JWT_SECRET')
    SUPPORTED_AUDIO_EXTS = ('wav', 'mp3', 'flac', 'aac', 'm4a', 'ogg')

    class Supabase:
        URL: str = require_env('SUPABASE_URL')
        JWT_KEY: str = require_env('SUPABASE_JWT_KEY')
        ANON_KEY: str = require_env('SUPABASE_ANON_KEY')
        SERVICE_ROLE: str = require_env('SUPABASE_SERVICE_ROLE')
        DATABASE_URL: str = require_env('SUPABASE_SESSION_POOLER')
        STORAGE_URL: str = require_env('SUPABASE_STORAGE_URL')
        STORAGE_KEY_ID: str = require_env('SUPABASE_STORAGE_KEY_ID')
        STORAGE_SECRET: str = require_env('SUPABASE_STORAGE_SECRET')
        STORAGE_BUCKET_NAME: str = require_env(
            'SUPABASE_STORAGE_BUCKET_NAME'
        )

    class Telegram:
        TOKEN = optional_env('TELEGRAM_TOKEN', '')
        CHAT_ID = optional_env('TELEGRAM_CHAT_ID', '')
