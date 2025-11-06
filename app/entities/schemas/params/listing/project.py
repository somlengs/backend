from dataclasses import dataclass

from app.entities.schemas.params.listing.__base__ import ListingParam
from app.entities.types.enums.ordering import Ordering
from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.types.enums.sorting import ProjectSorting

@dataclass
class ProjectListingParams(ListingParam):
    project_name: str 
    status: ProcessingStatus | None
    
    sort: ProjectSorting
    order: Ordering
