from dataclasses import dataclass

@dataclass
class ListingParam:
    limit: int
    offset: int
