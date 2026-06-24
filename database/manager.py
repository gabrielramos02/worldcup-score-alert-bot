from datetime import datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select

class Team(SQLModel, table=True):
    id: int = Field(primary_key=True)
    team_name: str = Field(nullable=False)
    logo_url: str = Field(nullable=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

class Subscription(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    chat_id: str = Field(nullable=False)
    team_id: int = Field(nullable=False, foreign_key="team.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

engine = create_engine("sqlite:///database/database.db")


SQLModel.metadata.create_all(engine)


async def test_database():
    with Session(engine) as session:
        session.commit()


############# SUBSCRIPTIONS #############
async def add_subscription(chat_id: str, team_id: int):
    with Session(engine) as session:
        subscription = Subscription(
            chat_id=chat_id,
            team_id=team_id,
        )
        session.add(subscription)
        session.commit()


async def get_subscription_for_team(chat_id: str, team_id: int) -> bool:
    with Session(engine) as session:
        statement = select(Subscription).where(
            Subscription.chat_id == chat_id, Subscription.team_id == team_id
        )
        results = session.exec(statement)
        return results.first() is not None


async def remove_subscription(chat_id: str, team_id: int):
    with Session(engine) as session:
        statement = select(Subscription).where(
            Subscription.chat_id == chat_id, Subscription.team_id == team_id
        )
        results = session.exec(statement)
        subscription = results.first()
        if subscription:
            session.delete(subscription)
            session.commit()


####################################
################ TEAMS #############
async def get_teams() -> list[Team]:
    with Session(engine) as session:
        statement = select(Team)
        results = session.exec(statement)
        return list(results.all())


async def get_team(team_id: int) -> Team | None:
    with Session(engine) as session:
        statement = select(Team).where(Team.id == team_id)
        results = session.exec(statement)
        return results.first()


async def add_team(team_id: int, team_name: str, logo_url: str):
    with Session(engine) as session:
        team = Team(
            id=team_id,
            team_name=team_name,
            logo_url=logo_url,
        )
        _ = session.merge(team)  # Use merge to avoid duplicates
        session.commit()


async def remove_team(team_id: int):
    with Session(engine) as session:
        statement = select(Team).where(Team.id == team_id)
        results = session.exec(statement)
        team = results.first()
        if team:
            session.delete(team)
            session.commit()


###################################
