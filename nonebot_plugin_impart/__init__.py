"""插件入口"""
import contextlib
from re import I
from nonebot import on_command, on_regex, require
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from .handle import impart
from .config import Config
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

scheduler.add_job(impart.penalties_and_resets, "cron", hour = 0, misfire_grace_time = 600)

on_command(
    "pk",
    aliases={"对决"},
    rule=Config.rule,
    priority=20,
    block=False,
    handlers=[impart.pk],
)

on_regex(
    "^(打胶|开导)$", 
    priority=20, 
    block=True, 
    handlers=[impart.dajiao]
)

on_command(
    "嗦牛子", 
    aliases={"嗦", "suo"},
    priority=20, 
    block=True, 
    handlers=[impart.suo]
)

on_command(
    "查询", 
    priority=20, 
    block=False, 
    handlers=[impart.queryjj]
)

on_command(
    "jj排行榜",
    aliases={"jj排名", "jj榜单", "jjrank", "牛子排行榜"},
    priority=20,
    block=True,
    handlers=[impart.jjrank],
)
on_regex(
    r"^(日群友|透群友|日群主|透群主|日管理|透管理)",
    flags=I,
    priority=20,
    block=True,
    handlers=[impart.yinpa],
)

on_regex(
    r"^(开始银趴|开启银趴|关闭银趴|禁止银趴|开始impart|开启impart|关闭impart|禁止impart)",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    flags=I,
    priority=10,
    block=True,
    handlers=[impart.open_module],
)

on_command(
    "注入查询",
    aliases={"摄入查询", "射入查询"},
    priority=20,
    block=True,
    handlers=[impart.query_injection],
)

on_command(
    "银趴介绍", 
    aliases={"impart介绍", "银趴帮助"},
    priority=20, 
    block=True,
    handlers=[impart.yinpa_introduce]
)

with contextlib.suppress(Exception):
    from nonebot.plugin import PluginMetadata

    __plugin_meta__ = PluginMetadata(
        name="nonebot_plugin_impart",
        usage=config.usage,
        description="NoneBot2 银趴插件 Plus",
        type="application",
        homepage="https://github.com/YuuzukiRin/nonebot_plugin_impart",
        config=Config,
        supported_adapters={"~onebot.v11"},
        extra={
            "priority": 20,
        },
    )
