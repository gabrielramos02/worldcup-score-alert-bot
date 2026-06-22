from datetime import datetime

from sqlmodel import Field, Session, SQLModel, create_engine


class Subscription(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    chat_id: str = Field(nullable=False)
    team_id : int = Field(nullable=False)
    team_name : str = Field(nullable=False)
    created_at: datetime  = Field(default_factory=lambda: datetime.now(), nullable=False)



engine = create_engine("sqlite:///database/database.db")


SQLModel.metadata.create_all(engine)

async def test_database():
    with Session(engine) as session:
        session.commit()
