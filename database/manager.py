from datetime import datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select


class Subscription(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    chat_id: str = Field(nullable=False)
    team_id: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)


engine = create_engine("sqlite:///database/database.db")


SQLModel.metadata.create_all(engine)


async def test_database():
    with Session(engine) as session:
        session.commit()


async def add_subscription(chat_id: str, team_id: int ):
    with Session(engine) as session:
        subscription = Subscription(
            chat_id=chat_id,
            team_id=team_id,
        )
        session.add(subscription)
        session.commit()

async def get_subscription_for_team(chat_id: str, team_id: int) -> bool:
    with Session(engine) as session:
        statement = select(Subscription).where(Subscription.chat_id == chat_id, Subscription.team_id == team_id)
        results = session.exec(statement)
        return  results.first() is not None
