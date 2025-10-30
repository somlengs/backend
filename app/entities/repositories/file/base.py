# from __future__ import annotations

# from abc import ABC, abstractmethod


# from sqlalchemy.orm import Session, sessionmaker

# class FileRepo(ABC):
#     instance: FileRepo

#     @classmethod
    
#     def init(cls, repo: FileRepo) -> None:
#         cls.instance = repo

#     @abstractmethod
#     def get_session(self) -> sessionmaker[Session]:
#         ...
        
#     @abstractmethod
#     def 