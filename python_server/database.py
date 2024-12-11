import pickle
from typing import Optional
from datetime import datetime
from sqlmodel import Field, Session, SQLModel, create_engine, select


# SQLModel Request table
class Request(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hash: str = Field(unique=True)
    content: Optional[bytes] = None
    timestamp: str
    status: str


class DatabaseHandler:
    def __init__(self, db_url="sqlite:///./database.db"):
        self.engine = create_engine(db_url, echo=False)
        SQLModel.metadata.create_all(self.engine)

    def __enter__(self):
        """
        Initializes the database session and returns the instance.
        """
        self.session = Session(self.engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures the session is properly closed.
        """
        self.session.close()

    def get_request(self, hash: str):
        """
        Returns the request with the given hash if it exists.
        """
        statement = select(Request).where(Request.hash == hash)
        result = self.session.exec(statement).first()

        if result:
            return True, pickle.loads(result.content) if result.content else None

        return False, None

    def get_all_requests(self):
        """
        Returns all requests with their status.
        """
        statement = select(Request.id, Request.timestamp, Request.status)
        results = self.session.exec(statement).all()
        return results

    def add_new_request(self, hash: str):
        """
        Adds a new request to the database and returns the ID of the request.
        """
        new_request = Request(
            hash=hash,
            content=None,
            timestamp=datetime.now().isoformat(),
            status="PENDING",
        )
        self.session.add(new_request)
        self.session.commit()
        self.session.refresh(new_request)
        return new_request.id

    def update_request_result(self, request_id: int, result):
        """
        Updates the request with the given ID with the result.
        """
        statement = select(Request).where(Request.id == request_id)
        request = self.session.exec(statement).first()

        if request:
            request.content = pickle.dumps(result)
            request.status = "COMPLETED"
            self.session.add(request)
            self.session.commit()

    def get_response(self, request_id: int):
        """
        Returns the response for a completed request.
        """
        statement = select(Request).where(Request.id == request_id)
        request = self.session.exec(statement).first()

        if not request or request.status != "COMPLETED":
            return None

        return pickle.loads(request.content) if request.content else None
