import asyncio
from pathlib import Path
from typing import override
import random

from app.entities.types.transcription_result import TranscriptionResult
from .base import STTRepo

class MockSTTRepo(STTRepo):

    @override
    async def transcribe_from_sss_path(self, path: str) -> TranscriptionResult:
        await asyncio.sleep( 20 + (30 * random.random()))
        content = 'កន្ទឺយក៏ដើរទៅផ្ទះវិញដោយគិតថាខ្លួននឹងត្រស្លាប់ក៏ដើរផងយំផង។ដើរបានពាក់កណ្ដាលផ្លូវក៏ជួបនឹងទន្សាយ។ទន្សាយសួរ៖«តើបងកន្ទឺយមានរឿងអ្វីបានជាយំ?»   «បាទ!ខ្ញុំយំព្រោះខ្លានិយាយថានឹងសម្លាប់ខ្ញុំនៅថ្ងៃនេះ»ខ្លាចស្អីខ្លា!ចូរបងរកចេកទុំមួយស្និតមក ខ្ញុំនឹងជួយបងអោយរួចពីសេចក្ដីស្លាប់»។ដោយកន្ទឺយចង់រស់រានមានជីវិតទៀត ក៏ទៅីរកចេកទុំអោយទន្សាយ។ពេលបានចេកទុំហើយទន្សាយសុីយ៉ាងឆ្អែតនៅកន្លែងរូងថ្មមួយ។'
        return TranscriptionResult(
            status_code=201,
            transcription=content,
            audio_filename=path,
            model_used='mock'
        )

    @override
    async def transcribe_from_bytes(self, data: bytes, format: str = 'wav') -> TranscriptionResult:
        ...

    @override
    async def transcribe_from_local_path(self, path: Path) -> TranscriptionResult:
        ...
