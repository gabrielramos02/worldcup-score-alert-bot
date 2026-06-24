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

class Live_Match(SQLModel, table=True):
    match_id: str = Field(nullable=False, primary_key=True)
    home_team_id: int = Field(nullable=False, foreign_key="team.id")
    away_team_id: int = Field(nullable=False, foreign_key="team.id")
    home_score: int = Field(default=0, nullable=False)
    away_score: int = Field(default=0, nullable=False)
    clock_time: str = Field(default="0'", nullable=True)
    is_live: bool = Field(default=False, nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

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

async def get_subscribers(team_id: int) -> list[str]:
    with Session(engine) as session:
        statement = select(Subscription.chat_id).where(Subscription.team_id == team_id)
        results = session.exec(statement)
        return [row[0] for row in results.all()]

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

async def get_subscription(chat_id: str) -> list[Subscription]:
    with Session(engine) as session:
        statement = select(Subscription).where(Subscription.chat_id == chat_id)
        results = session.exec(statement)
        return list(results.all())


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
        _ = session.merge(team)  
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
