from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from os import getenv
from database.models import Base

engine=create_async_engine(getenv('LITE_DB'))
session_maker=async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

async def create_db():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)
        
async def drop_db():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.drop_all)