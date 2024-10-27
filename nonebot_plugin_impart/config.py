"""配置和工具函数"""
import random
import time
from typing import Union
from pydantic import BaseModel
from nonebot.adapters.onebot.v11 import GroupMessageEvent

class Config(BaseModel):
    usage = """impart功能说明:
[嗦牛子|嗦] 
给目标牛牛增加长度,通过at选择对象,没有at时目标是自己
[打胶|开导] 
给自己牛牛增加长度
[pk|对决] 
通过random实现输赢,胜利方获取败方随机数/2的牛牛长度;初始胜率为50%,pk后胜方胜率-1%,败方胜率+1%
[查询] 
目标牛牛长度, 自己或者他人,通过艾特选择对象,没有at时目标是自己
[jj排行榜|jj排名|jj榜单|jjrank] 
字面意思,输出倒数五位和前五位,以及自己的排名
[开启银趴|禁止银趴|开始impart|关闭impart] 
由管理员|群主|SUPERUSERS开启或者关闭impart
[日群友|透群友|日群主|透群主|日管理|透管理] 
字面意思,当使用透群友的时候如果at了人那么直接指定
[注入查询|摄入查询|射入查询] 
查询目标被透注入的量,后接(历史|全部),可查看总被摄入的量,通过at选择对象,没有at时目标是自己
[银趴介绍|impart介绍] 
输出impart插件的命令列表
<牛牛长度超过25时会触发神秘任务>
"""
    not_allow = '群内还未开启impart游戏, 请管理员或群主发送"开始银趴", "禁止银趴"以开启/关闭该功能'
    jj_variable = ["牛子", "牛牛", "newnew"]
    cd_data = {}  # 冷却数据
    pk_cd_data = {}  # pk冷却数据
    suo_cd_data = {}  # 嗦冷却数据
    ejaculation_cd = {}  # 注入CD
    dj_cd_time: int = 300  # 打胶冷却时间
    pk_cd_time: int = 60  # pk冷却时间
    suo_cd_time: int = 300  # 嗦冷却时间
    fuck_cd_time: int = 3600  # 透群友冷却时间
    ban_id_list: str = "123456" # 白名单列表
    ban_id_set: set[str] = set(ban_id_list.split(",")) if ban_id_list else set() 
    botname_set: set[str] = ["YUUZUKI"]
    botname: str = next(iter(botname_set))

    @staticmethod
    async def rule(event: GroupMessageEvent) -> bool:
        """rule检查, 是否有at"""
        msg = event.get_message()
        return next(
            (msg_seg.data["qq"] != "all" for msg_seg in msg if msg_seg.type == "at"),
            False,
        )

    @staticmethod
    async def get_at(event: GroupMessageEvent) -> str:
        """获取at的qq号, 不存在则返回寄, 类型为str"""
        msg = event.get_message()
        return next(
            (
                "寄" if msg_seg.data["qq"] == "all" else str(msg_seg.data["qq"])
                for msg_seg in msg
                if msg_seg.type == "at"
            ),
            "寄",
        )

    async def cd_check(self, uid: str) -> bool:
        """打胶的冷却检查"""
        cd = (
            time.time() - self.cd_data[uid]
            if uid in self.cd_data
            else self.dj_cd_time + 1
        )
        return cd > self.dj_cd_time

    async def pkcd_check(self, uid: str) -> bool:
        """pk冷却检查"""
        cd = (
            time.time() - self.pk_cd_data[uid]
            if uid in self.pk_cd_data
            else self.pk_cd_time + 1
        )
        return cd > self.pk_cd_time

    async def suo_cd_check(self, uid: str) -> bool:
        """嗦牛子冷却检查"""
        cd = (
            time.time() - self.suo_cd_data[uid]
            if uid in self.suo_cd_data
            else self.suo_cd_time + 1
        )
        return cd > self.suo_cd_time

    async def fuck_cd_check(self, event: GroupMessageEvent) -> bool:
        """透群友检查"""
        uid = event.get_user_id()
        cd = (
            time.time() - self.ejaculation_cd[uid]
            if uid in self.ejaculation_cd
            else self.fuck_cd_time + 1
        )
        return (
            cd > self.fuck_cd_time
            or event.get_user_id() in nonebot.get_driver().config.superusers
        )

    @staticmethod
    def get_random_num() -> float:
        """获取随机数 0.1的概率是1-2随机获取, 剩下0.9是0-1"""
        rand_num = random.random()
        rand_num = random.uniform(0, 1) if rand_num > 0.1 else random.uniform(1, 2)
        return round(rand_num, 3)
        
    @staticmethod
    def plugin_usage():
        """返回功能说明"""
        return Config().usage

