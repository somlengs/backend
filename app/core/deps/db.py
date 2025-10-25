
from app.entities.repositories.project.base import ProjectRepo

def get_db():
    SL = ProjectRepo.instance.get_session()

    with SL() as db:
        yield db
