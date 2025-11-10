from dataclasses import dataclass

from app.entities.schemas.params.listing.__base__ import ListingParam
from app.entities.types.enums.ordering import Ordering
from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.types.enums.sorting import AudioFileSorting

@dataclass
class AudioFileListingParams(ListingParam):
    file_name: str
    status: ProcessingStatus | None
    
    sort: AudioFileSorting
    order: Ordering
