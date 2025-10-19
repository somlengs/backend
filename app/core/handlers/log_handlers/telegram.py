from logging import Handler, LogRecord, Formatter
from typing import override


from telegram import Bot

from app.core.config import Config
import asyncio


class TelegramLogHandler(Handler):
    bot: Bot

    LOG_FORMAT = f"""
```
[%(asctime)s] [%(name)s]
Level:    %(levelname)s
Env:      {Config.ENVIRONMENT}
Message:  %(message)s
Function: %(funcName)s
Process:  %(process)d | Thread: %(threadName)s
```
"""

    def __init__(self, level: int | str = 0) -> None:
        """Log handler that send the log to a Telegram chat"""
        super().__init__(level)
        self.bot = Bot(Config.Telegram.TOKEN)
        formatter = Formatter(self.LOG_FORMAT, datefmt="%d-%m-%Y %H:%M:%S")
        self.setFormatter(formatter)

    @override
    def emit(self, record: LogRecord) -> None:
        try:
            message = self.format(record)
            asyncio.get_running_loop().create_task(self.send_markdown(message))

        except Exception:
            self.handleError(record)

    async def send_message(self, message: str) -> None:
        await self.bot.send_message(Config.Telegram.CHAT_ID, message)

    async def send_markdown(self, message: str, disable_notification: bool = False) -> None:
        await self.bot.send_message(
            Config.Telegram.CHAT_ID,
            message,
            parse_mode='MarkdownV2',
            disable_notification=disable_notification
        )
