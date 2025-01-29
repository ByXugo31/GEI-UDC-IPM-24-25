from sqlmodel import create_engine, Session


SQLITE_FILE_NAME = "medications.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session