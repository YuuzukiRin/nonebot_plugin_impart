"""数据库操作模块"""
import os
import random
import time
import sqlalchemy as sa
from typing import Dict, List

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    String,
    select,
    update,
    delete
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path
from nonebot import require
require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

DATA_PATH: Path = store.get_plugin_data_dir()

engine = create_async_engine(f"sqlite+aiosqlite:///{DATA_PATH}/impart.db")
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class UserData(Base):
    """用户数据表"""

    __tablename__ = "userdata"

    userid = Column(Integer, primary_key=True, index=True)
    jj_length = Column(Float, nullable=False)
    last_masturbation_time = Column(Integer, nullable=False, default=0)
    win_probability = Column(Float, nullable=False, default=0.5)  # 默认胜率为0.5
    is_challenging = Column(Boolean, nullable=False, default=False)  # 是否在挑战状态
    challenge_completed = Column(Boolean, nullable=False, default=False)  # 是否完成挑战
    is_near_zero = Column(Boolean, nullable=False, default=False)
    is_zero_or_neg = Column(Boolean, nullable=False, default=False)


class GroupData(Base):
    """群数据表"""

    __tablename__: str = "groupdata"

    groupid = Column(Integer, primary_key=True, index=True)
    allow = Column(Boolean, nullable=False)


class EjaculationData(Base):
    """被注入数据表"""

    __tablename__: str = "ejaculation_data"

    id = Column(Integer, primary_key=True)
    userid = Column(Integer, nullable=False, index=True)
    date = Column(String(20), nullable=False)
    volume = Column(Float, nullable=False)


async def check_and_add_column():
    """检查是否存在win_probability、is_challenging、challenge_completed列, 若无则添加"""
    async with engine.begin() as conn:
        result = await conn.execute(sa.text("PRAGMA table_info(userdata)"))        
        columns = [row[1] for row in result] 
        if 'win_probability' not in columns:
            await conn.execute(sa.text("ALTER TABLE userdata ADD COLUMN win_probability FLOAT DEFAULT 0.5"))
        if 'is_challenging' not in columns:
            await conn.execute(sa.text("ALTER TABLE userdata ADD COLUMN is_challenging BOOLEAN DEFAULT FALSE"))
        if 'challenge_completed' not in columns:
            await conn.execute(sa.text("ALTER TABLE userdata ADD COLUMN challenge_completed BOOLEAN DEFAULT FALSE"))
        if 'is_near_zero' not in columns:
            await conn.execute(sa.text("ALTER TABLE userdata ADD COLUMN is_near_zero BOOLEAN DEFAULT FALSE"))      
        if 'is_zero_or_neg' not in columns:
            await conn.execute(sa.text("ALTER TABLE userdata ADD COLUMN is_zero_or_neg BOOLEAN DEFAULT FALSE"))
            
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await check_and_add_column()
    
    
async def update_challenge_status(userid: int) -> str:
    """根据用户的jj_length、is_challenging和challenge_completed状态更新用户的挑战状态和胜率"""

    async with async_session() as s:
        result = await s.execute(select(UserData).where(UserData.userid == userid))
        user = result.scalar()

        if not user:
            return "user_not_found"

        jj_length = user.jj_length
        is_challenging = user.is_challenging
        challenge_completed = user.challenge_completed
        win_probability = user.win_probability
        is_near_zero = user.is_near_zero
        is_zero_or_neg = user.is_zero_or_neg

        response = ""

        if not is_challenging and not challenge_completed and 25 <= jj_length < 30:
            user.is_challenging = True
            user.win_probability *= 0.8
            response = "challenge_started_low_win"

        elif not is_challenging and not challenge_completed and jj_length >= 30:
            user.challenge_completed = True
            response = "challenge_completed"

        elif is_challenging and not challenge_completed and jj_length < 25:
            user.win_probability *= 1.25
            user.jj_length -= 5
            user.is_challenging = False
            response = "challenge_failed_high_win"

        elif is_challenging and not challenge_completed and jj_length >= 30:
            user.win_probability *= 1.25
            user.is_challenging = False
            user.challenge_completed = True
            response = "challenge_success_high_win"
            
        elif is_challenging and 25 <= jj_length < 30:
            response = "is_challenging"
            
        elif challenge_completed and 25 <= jj_length < 30:
            response = "challenge_completed"
            
        elif challenge_completed and jj_length < 25:
            user.jj_length -= 5
            user.challenge_completed = False
            response = "challenge_completed_reduce"                    
            
        elif not is_near_zero and 0 < jj_length <= 5:
            user.is_near_zero = True
            response = "length_near_zero"
            
        elif is_near_zero and (jj_length <= 0 or jj_length > 5):
            user.is_near_zero = False
            
        elif not is_zero_or_neg and jj_length <= 0:
            user.is_zero_or_neg = True
            response = "length_zero_or_negative"
        
        elif is_zero_or_neg and jj_length > 0:
            user.is_zero_or_neg = False
            
        await s.commit()
        return response


async def add_new_user(userid: int) -> None:
    """插入一个新用户, 默认长度是10.0"""
    async with async_session() as s:
        s.add(
            UserData(
                userid=userid, jj_length=10.0, last_masturbation_time=int(time.time()), win_probability=0.5
            )
        )
        await s.commit()


async def update_activity(userid: int) -> None:
    """更新用户活跃时间"""
    if not await is_in_table(userid):
        await add_new_user(userid)
    async with async_session() as s:
        await s.execute(
            update(UserData).where(UserData.userid == userid).values(
                last_masturbation_time=int(time.time())
            )
        )
        await s.commit()


async def get_jj_length(userid: int) -> float:
    """传入用户id, 返还数据库中对应的jj长度"""
    async with async_session() as s:
        result = await s.execute(select(UserData.jj_length).filter(UserData.userid == userid))
        return result.scalar() or 0.0


async def set_jj_length(userid: int, length: float) -> None:
    """传入一个用户id以及需要增加的长度, 在数据库内累加, 用这个函数前一定要先判断用户是否在表中"""
    async with async_session() as s:
        current_length = await get_jj_length(userid)
        await s.execute(
            update(UserData).where(UserData.userid == userid).values(
                jj_length=round(current_length + length, 3),
                last_masturbation_time=int(time.time()),
            )
        )
        await s.commit()


async def get_win_probability(userid: int) -> float:
    """传入用户id, 返还数据库中对应的获胜概率"""
    async with async_session() as s:
        result = await s.execute(select(UserData.win_probability).filter(UserData.userid == userid))
        return result.scalar() or 0.5


async def set_win_probability(userid: int, probability_change: float) -> None:
    """传入一个用户id以及需要增加的获胜率, 在数据库内累加, 用这个函数前一定要先判断用户是否在表中"""
    async with async_session() as s:
        current_probability = await get_win_probability(userid)
        await s.execute(
            update(UserData).where(UserData.userid == userid).values(
                win_probability=round(current_probability + probability_change, 3),
                last_masturbation_time=int(time.time()),
            )
        )
        await s.commit()


async def check_group_allow(groupid: int) -> bool:
    """检查群是否允许, 传入群号, 类型是int"""
    async with async_session() as s:
        result = await s.execute(select(GroupData.allow).filter(GroupData.groupid == groupid))
        return result.scalar() or False


async def set_group_allow(groupid: int, allow: bool) -> None:
    """设置群聊开启或者禁止银趴, 传入群号, 类型是int, 以及allow, 类型是bool"""
    async with async_session() as session:
        # 检查该 groupid 是否已存在
        result = await session.execute(select(GroupData).where(GroupData.groupid == groupid))
        existing_group = result.scalar_one_or_none()  # 获取单个记录或 None
        if existing_group is None:
            # 如果不存在，则插入新记录
            new_group_data = GroupData(groupid=groupid, allow=allow)
            session.add(new_group_data)
        else:
            # 如果已存在，更新 allow 字段
            existing_group.allow = allow
        await session.commit()


def get_today() -> str:
    """获取当前年月日格式: 2024-10-20"""
    return time.strftime("%Y-%m-%d", time.localtime())


async def insert_ejaculation(userid: int, volume: float) -> None:
    """插入一条注入的记录"""
    now_date = get_today()
    async with async_session() as s:
        result = await s.execute(
            select(EjaculationData.volume)
            .filter(EjaculationData.userid == userid, EjaculationData.date == now_date)
        )
        current_volume = result.scalar()
        if current_volume is not None:
            await s.execute(
                update(EjaculationData)
                .where(EjaculationData.userid == userid, EjaculationData.date == now_date)
                .values(volume=round(current_volume + volume, 3))
            )
        else:
            s.add(EjaculationData(userid=userid, date=now_date, volume=volume))
        await s.commit()


async def get_ejaculation_data(userid: int) -> List[Dict]:
    """获取一个用户的所有注入记录"""
    async with async_session() as s:
        result = await s.execute(select(EjaculationData).filter(EjaculationData.userid == userid))
        return [{"date": row.date, "volume": row.volume} for row in result.scalars()]


async def get_today_ejaculation_data(userid: int) -> float:
    """获取用户当日的注入量"""
    async with async_session() as s:
        result = await s.execute(
            select(EjaculationData.volume)
            .filter(EjaculationData.userid == userid, EjaculationData.date == get_today())
        )
        return result.scalar() or 0.0


async def punish_all_inactive_users() -> None:
    """所有不活跃的用户, 即上次打胶时间超过一天的用户, 所有jj_length大于1将受到减少0--1随机的惩罚"""
    async with async_session() as s:
        result = await s.execute(select(UserData).filter(UserData.last_masturbation_time < (time.time() - 86400), UserData.jj_length > 1))
        for user in result.scalars():
            user.jj_length = round(user.jj_length - random.random(), 3)
        await s.commit()


async def get_sorted() -> List[Dict]:
    """获取所有用户的jj长度, 并且按照从大到小排序"""
    async with async_session() as s:
        result = await s.execute(select(UserData).order_by(UserData.jj_length.desc()))
        return [{"userid": user.userid, "jj_length": user.jj_length} for user in result.scalars()]
