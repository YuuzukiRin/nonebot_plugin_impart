"""数据库操作模块"""
import os
import random
import time
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

    __tablename__: str = "userdata"

    userid = Column(Integer, primary_key=True, index=True)
    jj_length = Column(Float, nullable=False)
    last_masturbation_time = Column(Integer, nullable=False, default=0)
    win_probability = Column(Float, nullable=False, default=0.5)  # 默认胜率为0.5


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


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def is_in_table(userid: int) -> bool:
    """传入一个userid，判断是否在表中"""
    async with async_session() as s:
        result = await s.execute(select(UserData).filter(UserData.userid == userid))
        return bool(result.scalar())


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
    async with async_session() as s:
        if not await check_group_allow(groupid):
            s.add(GroupData(groupid=groupid, allow=False))
        await s.execute(
            update(GroupData).where(GroupData.groupid == groupid).values(allow=allow)
        )
        await s.commit()


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
