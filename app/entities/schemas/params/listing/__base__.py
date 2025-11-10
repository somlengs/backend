from dataclasses import dataclass

from sqlalchemy.orm import Query

@dataclass
class ListingParam:
    limit: int
    page: int
