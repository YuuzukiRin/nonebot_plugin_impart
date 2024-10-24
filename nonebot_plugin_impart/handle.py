"""matcher的handle模块"""
import asyncio
import random
import time
from random import choice
from typing import Dict, List, Tuple
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexGroup

from .data_sheet import (
    add_new_user,
    check_group_allow,
    get_ejaculation_data,
    get_jj_length,
    get_sorted,
    get_today_ejaculation_data,
    insert_ejaculation,
    is_in_table,
    punish_all_inactive_users,
    set_group_allow,
    set_jj_length,
    update_activity,
    get_win_probability,
    set_win_probability,
)
from .draw_img import draw_bar_chart
from nonebot import get_plugin_config
from .config import Config
plugin_config = get_plugin_config(Config)

class Impart:
    penalties_impact: bool = getattr(get_driver().config, "isalive", False)  # 重置每日活跃度

    @staticmethod
    def penalties_and_resets() -> None:
        """重置每日活跃度"""
        if Impart.penalties_impact:
            punish_all_inactive_users()

    @staticmethod
    async def pk(matcher: Matcher, event: GroupMessageEvent) -> None:
        """pk的响应器"""
        if not check_group_allow(event.group_id):
            await matcher.finish(plugin_config.not_allow, at_sender=True)

        uid: str = event.get_user_id()
        allow: bool = await plugin_config.pkcd_check(uid)  # CD是否允许pk
        if not allow:  # 如果不允许pk, 则返回
            await matcher.finish(
                f"你已经pk不动了喵, 请等待{round(plugin_config.pk_cd_time-(time.time() - plugin_config.pk_cd_data[uid]),3)}秒后再pk喵",
                at_sender=True,
            )

        plugin_config.pk_cd_data.update({uid: time.time()})  # 更新CD时间
        at = await plugin_config.get_at(event)  # 获取at的id, 类型为str
        if at == uid:  # 如果at的id和uid相同, 则返回
            await matcher.finish("你不能pk自己喵", at_sender=True)

        # 执行pk逻辑
        if is_in_table(userid=int(uid)) and is_in_table(int(at)):  # 如果两个都在userdata里面
            random_num = random.random()  # 生成一个随机数

            if random_num < get_win_probability(userid=int(uid)):  # 根据胜率决定胜负
                set_win_probability(int(uid), -0.01)  # 己方，减少1%的获胜概率
                set_win_probability(int(at), 0.01)  # 对方，增加1%的获胜概率
                random_num: float = plugin_config.get_random_num()  # 重新生成一个随机数
                if get_jj_length(int(uid)) < 25 and get_jj_length(int(uid)) + random_num / 2 >= 25:
                    set_jj_length(int(uid), random_num / 2)
                    current_probability = get_win_probability(int(uid))  # 获取当前的获胜概率
                    new_probability = current_probability * 0.80
                    difference = current_probability - new_probability
                    set_win_probability(int(uid), -difference)
                    if get_jj_length(int(at)) >= 25 and get_jj_length(int(at)) - random_num / 2 < 25:
                        current_probability = get_win_probability(int(at))
                        new_probability = current_probability * 1.25
                        difference = new_probability - current_probability 
                        set_win_probability(int(at), difference)                        
                        set_jj_length(int(at), -random_num - 5)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n检测到你的{choice(plugin_config.jj_variable)}长度超过25cm，已为你开启✨“登神长阶”✨，你现在的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请以将{choice(plugin_config.jj_variable)}长度提升至30cm为目标与他人pk吧!\n由于你对决的胜利，{plugin_config.botname}检测到TA的{choice(plugin_config.jj_variable)}长度已不足25cm，很遗憾，TA的登神挑战失败，{plugin_config.botname}替TA感谢你的鞭策喵！\nTA的{choice(plugin_config.jj_variable)}长度缩短了5cm喵，获胜概率已恢复喵！",
                            at_sender=True,
                        )
                    elif get_jj_length(int(at)) > 0 and get_jj_length(int(at)) - random_num <= 0:                       
                        set_jj_length(int(at), -random_num)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n检测到你的{choice(plugin_config.jj_variable)}长度超过25cm，已为你开启✨“登神长阶”✨，你现在的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请以将{choice(plugin_config.jj_variable)}长度提升至30cm为目标与他人pk吧!\n由于你对决的胜利，{plugin_config.botname}检测到TA已经变成女孩子了喵！",
                            at_sender=True,
                        )
                    else:
                        set_jj_length(int(at), -random_num)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n检测到你的{choice(plugin_config.jj_variable)}长度超过25cm，已为你开启✨“登神长阶”✨，你现在的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请以将{choice(plugin_config.jj_variable)}长度提升至30cm为目标与他人pk吧！",
                            at_sender=True,
                        )
                    
                elif get_jj_length(int(uid)) < 30 and get_jj_length(int(uid)) + random_num / 2 >= 30:
                    set_jj_length(int(uid), random_num / 2)
                    current_probability = get_win_probability(int(uid))
                    new_probability = current_probability * 1.25
                    difference = new_probability - current_probability
                    set_win_probability(int(uid), difference)
                    if get_jj_length(int(at)) >= 25 and get_jj_length(int(at)) - random_num / 2 < 25:
                        current_probability = get_win_probability(int(at))
                        new_probability = current_probability * 1.25
                        difference = new_probability - current_probability
                        set_win_probability(int(at), difference)                        
                        set_jj_length(int(at), -random_num - 5)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n🎉恭喜你完成登神挑战🎉\n你的{choice(plugin_config.jj_variable)}长度已超过30cm，授予你🎊“牛々の神”🎊称号\n你的获胜概率已恢复，“打胶”与“嗦”指令已重新开放，切记不忘初心，继续冲击更高的境界喵！\n由于你对决的胜利，{plugin_config.botname}检测到TA的{choice(plugin_config.jj_variable)}长度已不足25cm，很遗憾，TA的登神挑战失败，{plugin_config.botname}替TA感谢你的鞭策喵！\nTA的{choice(plugin_config.jj_variable)}长度缩短了5cm喵，获胜概率已恢复喵！",
                            at_sender=True,
                        )
                    elif get_jj_length(int(at)) > 0 and get_jj_length(int(at)) - random_num <= 0:                       
                        set_jj_length(int(at), -random_num)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n🎉恭喜你完成登神挑战🎉\n你的{choice(plugin_config.jj_variable)}长度已超过30cm，授予你🎊“牛々の神”🎊称号\n你的获胜概率已恢复，“打胶”与“嗦”指令已重新开放，切记不忘初心，继续冲击更高的境界喵！\n由于你对决的胜利，{plugin_config.botname}检测到TA已经变成女孩子了喵！",
                            at_sender=True,
                        )                
                    else:
                        set_jj_length(int(at), -random_num)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n🎉恭喜你完成登神挑战🎉\n你的{choice(plugin_config.jj_variable)}长度已超过30cm，授予你🎊“牛々の神”🎊称号\n你的获胜概率已恢复，“打胶”与“嗦”指令已重新开放，切记不忘初心，继续冲击更高的境界喵！",
                            at_sender=True,
                        )

                else:
                    set_jj_length(int(uid), random_num / 2)
                    if get_jj_length(int(at)) >= 25 and get_jj_length(int(at)) - random_num < 25:
                        current_probability = get_win_probability(int(at))
                        new_probability = current_probability * 1.25
                        difference = new_probability - current_probability
                        set_win_probability(int(at), difference)                        
                        set_jj_length(int(at), -random_num - 5)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n由于你对决的胜利，{plugin_config.botname}检测到TA的{choice(plugin_config.jj_variable)}长度已不足25cm，很遗憾，TA的登神挑战失败，{plugin_config.botname}替TA感谢你的鞭策喵！\nTA的{choice(plugin_config.jj_variable)}长度缩短了5cm喵，获胜概率已恢复喵！",
                            at_sender=True,
                        )
                    elif get_jj_length(int(at)) > 0 and get_jj_length(int(at)) - random_num <= 0:                       
                        set_jj_length(int(at), -random_num)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n你的胜率现在降为{get_win_probability(userid=int(uid)):.0%}喵\n由于你对决的胜利，{plugin_config.botname}检测到TA已经变成女孩子了喵！",
                            at_sender=True,
                        )
                    else:
                        set_jj_length(int(at), -random_num)
                        await matcher.finish(
                            f"对决胜利喵, 你的{choice(plugin_config.jj_variable)}增加了{round(random_num/2,3)}cm喵, 对面则在你的阴影笼罩下减小了{random_num}cm喵\n你的胜率现在降为{get_win_probability(userid=int(uid)):.0%}喵",
                            at_sender=True,
                        )

            else:
                set_win_probability(int(uid), 0.01) # 己方，增加1%的获胜概率
                set_win_probability(int(at), -0.01) # 对方，减少1%的获胜概率
                random_num: float = plugin_config.get_random_num()
                if get_jj_length(int(uid)) >= 25 and get_jj_length(int(uid)) - random_num < 25:
                    set_jj_length(int(uid), -random_num)                    
                    current_probability = get_win_probability(int(uid))
                    new_probability = current_probability * 1.25
                    difference = new_probability - current_probability
                    set_win_probability(int(uid), difference)
                    set_jj_length(int(uid), -5)
                    if get_jj_length(int(at)) < 25 and get_jj_length(int(at)) + random_num / 2 >= 25:
                        current_probability = get_win_probability(int(at))
                        new_probability = current_probability * 0.80
                        difference = current_probability - new_probability
                        set_win_probability(int(at), -difference)                        
                        set_jj_length(int(at), random_num / 2)
                        await matcher.finish(
                            f"对决失败喵, 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n很遗憾，登神挑战失败，别气馁啦！\n你的{choice(plugin_config.jj_variable)}长度缩短了5cm喵，你的获胜概率已恢复喵！\n由于你对决的失败，触犯到了神秘的禁忌，{plugin_config.botname}检测到TA的{choice(plugin_config.jj_variable)}长度超过25cm，已为TA开启✨“登神长阶”✨，现在TA的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请通知TA以将牛子长度提升至30cm为目标与群友pk吧！",
                            at_sender=True,
                        )
                    elif get_jj_length(int(at)) <= 30 and get_jj_length(int(at)) + random_num / 2 > 30:
                        set_jj_length(int(at), random_num / 2)
                        set_jj_length(int(uid), -random_num)
                        current_probability = get_win_probability(int(at))
                        new_probability = current_probability * 1.25
                        difference = new_probability - current_probability
                        set_win_probability(int(at), difference)
                        await matcher.finish(
                            f"对决失败喵, 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n很遗憾，登神挑战失败，别气馁啦！\n你的{choice(plugin_config.jj_variable)}长度缩短了5cm喵，你的获胜概率已恢复喵！\n🎉恭喜你帮助TA完成登神挑战🎉\n你的牺牲使TA的{choice(plugin_config.jj_variable)}长度超过30cm，授予TA🎊“牛々の神”🎊称号\nTA的获胜概率已恢复，“打胶”与“嗦”指令已重新开放，请提醒TA要不忘初心，继续冲击更高的境界喵！",
                            at_sender=True,
                        )
                    else:
                        set_jj_length(int(at), random_num / 2)
                        set_jj_length(int(uid), -random_num)
                        await matcher.finish(
                            f"对决失败喵, 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n很遗憾，登神挑战失败，别气馁啦！\n你的{choice(plugin_config.jj_variable)}长度缩短了5cm喵，你的获胜概率已恢复喵！",
                            at_sender=True,
                        )
                else:
                    set_jj_length(int(uid), -random_num)
                    if get_jj_length(int(at)) < 25 and get_jj_length(int(at)) + random_num / 2 >= 25:
                        current_probability = get_win_probability(int(at))
                        new_probability = current_probability * 0.80
                        difference = current_probability - new_probability
                        set_win_probability(int(at), -difference)                        
                        set_jj_length(int(at), random_num / 2)
                        if get_jj_length(int(at)) <= 0:                       
                            await matcher.finish(
                                f"你醒啦, 你已经变成女孩子了！ 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n由于你对决的失败，触犯到了神秘的禁忌，{plugin_config.botname}检测到TA的{choice(plugin_config.jj_variable)}长度超过25cm，已为TA开启✨“登神长阶”✨，现在TA的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请通知TA以将牛子长度提升至30cm为目标与群友pk吧！",
                                at_sender=True,
                            ) 
                        else:    
                            await matcher.finish(
                                f"对决失败喵, 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n由于你对决的失败，触犯到了神秘的禁忌，{plugin_config.botname}检测到TA的{choice(plugin_config.jj_variable)}长度超过25cm，已为TA开启✨“登神长阶”✨，现在TA的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请通知TA以将牛子长度提升至30cm为目标与群友pk吧！",
                                at_sender=True,
                            )
                    elif get_jj_length(int(at)) < 30 and get_jj_length(int(at)) + random_num / 2 >= 30:
                        set_jj_length(int(at), random_num / 2)
                        current_probability = get_win_probability(int(at))
                        new_probability = current_probability * 1.25
                        difference = new_probability - current_probability
                        set_win_probability(int(at), difference)
                        if get_jj_length(int(at)) <= 0:                       
                            await matcher.finish(
                                f"你醒啦, 你已经变成女孩子了！ 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n🎉恭喜你帮助TA完成登神挑战🎉\n你的牺牲使TA的{choice(plugin_config.jj_variable)}长度超过30cm，授予TA🎊“牛々の神”🎊称号\nTA的获胜概率已恢复，“打胶”与“嗦”指令已重新开放，请提醒TA要不忘初心，继续冲击更高的境界喵！",
                                at_sender=True,
                            ) 
                        else:                        
                            await matcher.finish(
                                f"对决失败喵, 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n🎉恭喜你帮助TA完成登神挑战🎉\n你的牺牲使TA的{choice(plugin_config.jj_variable)}长度超过30cm，授予TA🎊“牛々の神”🎊称号\nTA的获胜概率已恢复，“打胶”与“嗦”指令已重新开放，请提醒TA要不忘初心，继续冲击更高的境界喵！",
                                at_sender=True,
                            )                            
                    else:
                        set_jj_length(int(at), random_num / 2)                        
                        if get_jj_length(int(uid)) <= 0:                       
                            await matcher.finish(
                                f"你醒啦, 你已经变成女孩子了！ 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n你的胜率现在升为{get_win_probability(userid=int(uid)):.0%}喵",
                                at_sender=True,
                            ) 
                        else:                         
                            await matcher.finish(
                                f"对决失败喵, 在对面{choice(plugin_config.jj_variable)}的阴影笼罩下你的{choice(plugin_config.jj_variable)}减小了{random_num}cm喵, 对面增加了{round(random_num/2,3)}cm喵\n你的胜率现在升为{get_win_probability(userid=int(uid)):.0%}喵",
                                at_sender=True,
                            )

        else:
            # 谁不在userdata里面, 就创建谁
            if is_in_table(userid=int(uid)):
                add_new_user(int(at))
            if is_in_table(userid=int(at)):
                add_new_user(int(uid))
            del plugin_config.pk_cd_data[uid]  # 删除CD时间
            await matcher.finish(
                f"你或对面还没有创建{choice(plugin_config.jj_variable)}喵, 咱全帮你创建了喵, 你们的{choice(plugin_config.jj_variable)}长度都是10cm喵",
                at_sender=True,
            )

    @staticmethod
    async def dajiao(matcher: Matcher, event: GroupMessageEvent) -> None:
        """打胶的响应器"""
        if not check_group_allow(event.group_id):
            await matcher.finish(plugin_config.not_allow, at_sender=True)
        uid: str = event.get_user_id()
        allow = await plugin_config.cd_check(uid)  # CD是否允许打胶
        if not allow:  # 如果不允许打胶, 则返回
            await matcher.finish(
                f"你已经打不动了喵, 请等待{round(plugin_config.dj_cd_time-(time.time() - plugin_config.cd_data[uid]),3)}秒后再打喵",
                at_sender=True,
            )
        plugin_config.cd_data.update({uid: time.time()})  # 更新CD时间
        if is_in_table(userid=int(uid)):  # 如果在userdata里面
            current_length = get_jj_length(int(uid))
            
            # 检查牛子长度是否符合要求
            if 25 <= current_length <= 30:
                await matcher.finish(
                    f"你的{choice(plugin_config.jj_variable)}长度在任务范围内，不允许打胶，请专心与群友pk！",
                    at_sender=True,
                )
                return
                
            random_num = plugin_config.get_random_num()  # 生成一个随机数            
            if get_jj_length(int(uid)) < 25 and get_jj_length(int(uid)) + random_num >= 25:
                set_jj_length(int(uid), random_num)  # 更新userdata
                current_probability = get_win_probability(int(uid))  # 获取当前的获胜概率
                new_probability = current_probability * 0.80
                difference = current_probability - new_probability
                set_win_probability(int(uid), -difference)
                await matcher.finish(
                            f"打胶结束喵, 你的{choice(plugin_config.jj_variable)}很满意喵, 长了{random_num}cm喵\n由于你无休止的打胶，触犯到了神秘的禁忌，{plugin_config.botname}检测到你的{choice(plugin_config.jj_variable)}长度超过25cm，已为你开启✨“登神长阶”✨，你现在的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请以将{choice(plugin_config.jj_variable)}长度提升至30cm为目标与他人pk吧！",
                            at_sender=True,
                        )
            else:
                set_jj_length(int(uid), random_num)
                await matcher.finish(
                    f"打胶结束喵, 你的{choice(plugin_config.jj_variable)}很满意喵, 长了{random_num}cm喵, 目前长度为{get_jj_length(int(uid))}cm喵",
                    at_sender=True,
                )
        else:
            add_new_user(int(uid))  # 创建用户
            await matcher.finish(
                f"你还没有创建{choice(plugin_config.jj_variable)}, 咱帮你创建了喵, 目前长度是10cm喵",
                at_sender=True,
            )

    @staticmethod
    async def suo(matcher: Matcher, event: GroupMessageEvent) -> None:
        """嗦牛子的响应器"""
        if not check_group_allow(event.group_id):
            await matcher.finish(plugin_config.not_allow, at_sender=True)
        uid: str = event.get_user_id()
        allow = await plugin_config.suo_cd_check(uid)  # CD是否允许嗦
        if not allow:  # 如果不允许嗦, 则返回
            await matcher.finish(
                f"你已经嗦不动了喵, 请等待{round(plugin_config.suo_cd_time-(time.time() - plugin_config.suo_cd_data[uid]),3)}秒后再嗦喵",
                at_sender=True,
            )
        plugin_config.suo_cd_data.update({uid: time.time()})  # 更新CD时间
        at: str = await plugin_config.get_at(event)  # 获取at的用户id, 类型为str
        if at == "寄":  # 如果没有at
            if is_in_table(userid=int(uid)):  # 如果在userdata里面
                current_length = get_jj_length(int(uid))
        
                # 检查牛子长度是否符合要求
                if 25 <= current_length < 30:
                    await matcher.finish(
                        f"你的{choice(plugin_config.jj_variable)}长度在任务范围内，不准嗦！请专心与群友pk！",
                        at_sender=True,
                    )
                    return
                random_num = plugin_config.get_random_num()  # 生成一个随机数                
                if get_jj_length(int(uid)) < 25 and get_jj_length(int(uid)) + random_num >= 25:
                    set_jj_length(int(uid), random_num)
                    current_probability = get_win_probability(int(uid))  # 获取当前的获胜概率
                    new_probability = current_probability * 0.80
                    difference = current_probability - new_probability
                    set_win_probability(int(uid), -difference)
                    await matcher.finish(
                        f"你的{choice(plugin_config.jj_variable)}很满意喵, 嗦长了{random_num}cm喵\n由于你无休止的嗦与被嗦，触犯到了神秘的禁忌，{plugin_config.botname}检测到你的{choice(plugin_config.jj_variable)}长度超过25cm，已为你开启✨“登神长阶”✨，你现在的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请以将{choice(plugin_config.jj_variable)}长度提升至30cm为目标与他人pk吧！",
                        at_sender=True,
                    )
                else:
                    set_jj_length(int(uid), random_num)
                    await matcher.finish(
                        f"你的{choice(plugin_config.jj_variable)}很满意喵, 嗦长了{random_num}cm喵, 目前长度为{get_jj_length(int(uid))}cm喵",
                        at_sender=True,
                    )
            else:  # 如果不在userdata里面
                add_new_user(int(uid))  # 创建用户
                del plugin_config.suo_cd_data[uid]  # 删除CD时间
                await matcher.finish(
                    f"你还没有创建{choice(plugin_config.jj_variable)}喵, 咱帮你创建了喵, 目前长度是10cm喵",
                    at_sender=True,
                )
        elif is_in_table(userid=int(at)):  # 如果在userdata里面
            current_length = get_jj_length(int(at))
        
            # 检查牛子长度是否符合要求
            if 25 <= current_length < 30:
                await matcher.finish(
                    f"TA的{choice(plugin_config.jj_variable)}长度在任务范围内，不准给TA嗦！",
                    at_sender=True,
                )
                return
            random_num = plugin_config.get_random_num()  # 生成一个随机数
            if get_jj_length(int(at)) < 25 and get_jj_length(int(at)) + random_num >= 25:
                # 更新userdata
                set_jj_length(int(at), random_num)
                current_probability = get_win_probability(int(at))  # 获取当前的获胜概率
                new_probability = current_probability * 0.80
                difference = current_probability - new_probability
                set_win_probability(int(at), -difference)
                await matcher.finish(
                    f"对方的{choice(plugin_config.jj_variable)}很满意喵, 嗦长了{random_num}cm喵\n由于你无休止的嗦，触犯到了神秘的禁忌，{plugin_config.botname}检测到TA的{choice(plugin_config.jj_variable)}长度超过25cm，已为TA开启✨“登神长阶”✨，现在TA的获胜概率变为当前的80%，且无法使用“打胶”与“嗦”指令，请通知TA以将牛子长度提升至30cm为目标与群友pk吧！",
                    at_sender=True,
                )
            else:
                set_jj_length(int(at), random_num)
                await matcher.finish(
                    f"对方的{choice(plugin_config.jj_variable)}很满意喵, 嗦长了{random_num}cm喵, 目前长度为{get_jj_length(int(at))}cm喵",
                    at_sender=True,
                )
        else:
            add_new_user(int(at))  # 创建用户
            del plugin_config.suo_cd_data[uid]  # 删除CD时间
            await matcher.finish(
                f"TA还没有创建{choice(plugin_config.jj_variable)}喵, 咱帮TA创建了喵, 目前长度是10cm喵",
                at_sender=True,
            )

    @staticmethod
    async def queryjj(matcher: Matcher, event: GroupMessageEvent) -> None:
        """查询某人jj的响应器"""
        if not check_group_allow(event.group_id):
            await matcher.finish(plugin_config.not_allow, at_sender=True)
        uid: str = event.get_user_id()  # 获取用户id, 类型为str
        at: str = await plugin_config.get_at(event)  # 获取at的用户id, 类型为str
        if at == "寄":  # 如果没有at
            if is_in_table(userid=int(uid)):  # 如果在userdata里面
                if get_jj_length(int(uid)) > 5:
                    await matcher.finish(
                        f"你的{choice(plugin_config.jj_variable)}目前长度为{get_jj_length(int(uid))}cm喵",
                        at_sender=True,
                    )
                elif 5 >= get_jj_length(int(uid)) > 1:
                    await matcher.finish(
                        f"你已经是xnn啦！\n你的{choice(plugin_config.jj_variable)}目前长度为{get_jj_length(int(uid))}cm喵",
                        at_sender=True,
                    )  
                elif 1 >= get_jj_length(int(uid)) > 0:
                    await matcher.finish(
                        f"你快要变成女孩子啦！\n你的{choice(plugin_config.jj_variable)}目前长度为{get_jj_length(int(uid))}cm喵",
                        at_sender=True,
                    )
                else:
                    await matcher.finish(
                        f"你已经是女孩子啦！\n你的{choice(plugin_config.jj_variable)}目前长度为{get_jj_length(int(uid))}cm喵",
                        at_sender=True,
                    )                    
            else:
                add_new_user(int(uid))  # 创建用户
                await matcher.finish(
                    f"你还没有创建{choice(plugin_config.jj_variable)}喵, 咱帮你创建了喵, 目前长度是10cm喵",
                    at_sender=True,
                )
        elif is_in_table(userid=int(at)):  # 如果在userdata里面
            if get_jj_length(int(at)) > 5:        
                await matcher.finish(
                    f"TA的{choice(plugin_config.jj_variable)}目前长度为{get_jj_length(int(at))}cm喵",
                    at_sender=True,
                )
            elif 5 >= get_jj_length(int(at)) > 1:        
                await matcher.finish(
                    f"TA已经是xnn啦！\nTA的{choice(plugin_config.jj_variable)}目前长度为{get_jj_length(int(at))}cm喵",
                    at_sender=True,
                )
            elif 1 >= get_jj_length(int(at)) > 0:        
                await matcher.finish(
                    f"TA快要变成女孩子啦！\nTA的{choice(plugin_config.jj_variable)}目前长度为{get_jj_length(int(at))}cm喵",
                    at_sender=True,
                )
            else:        
                await matcher.finish(
                    f"TA已经是女孩子啦！\nTA的{choice(plugin_config.jj_variable)}目前长度为{get_jj_length(int(at))}cm喵",
                    at_sender=True,
                )
        else:
            add_new_user(int(at))  # 创建用户
            await matcher.finish(
                f"TA还没有创建{choice(plugin_config.jj_variable)}喵, 咱帮他创建了喵, 目前长度是10cm喵",
                at_sender=True,
            )

    @staticmethod
    async def jjrank(bot: Bot, matcher: Matcher, event: GroupMessageEvent) -> None:
        """输出前五后五和自己的排名"""
        if not check_group_allow(event.group_id):
            await matcher.finish(utils.not_allow, at_sender=True)
        uid: int = event.user_id
        rankdata: List[Dict] = get_sorted()
        if len(rankdata) < 5:
            await matcher.finish("目前记录的数据量小于5, 无法显示rank喵")
        top5: List = rankdata[:5]  # 取前5
        last5: List = rankdata[-5:]  # 取后5
        # 获取自己的排名
        index: List = [i for i in range(len(rankdata)) if rankdata[i]["userid"] == uid]
        if not index:  # 如果用户没有创建JJ
            add_new_user(uid)
            await matcher.finish(
                f"你还没有创建{choice(utils.jj_variable)}看不到rank喵, 咱帮你创建了喵, 目前长度是10cm喵",
                at_sender=True,
            )
        # top5和end5的信息，然后获取其网名
        async with AsyncClient() as client:
            top5names = await asyncio.gather(
                *[utils.get_stranger_info(client, name["userid"]) for name in top5]
            )
            last5names = await asyncio.gather(
                *[utils.get_stranger_info(client, name["userid"]) for name in last5]
            )

        data = {top5names[i]: top5[i]["jj_length"] for i in range(len(top5))}
        for i in range(len(last5)):
            data[last5names[i]] = last5[i]["jj_length"]
        img_bytes = await draw_bar_chart.draw_bar_chart(data)
        reply2 = f"你的排名为{index[0]+1}喵"
        await matcher.finish(MessageSegment.image(img_bytes) + reply2, at_sender=True)

    @staticmethod
    async def yinpa_prehandle(
        bot: Bot,
        args: Tuple,
        matcher: Matcher,
        event: GroupMessageEvent,
    ) -> Tuple[int, str, str, list]:
        """透群员的预处理环节"""
        gid, uid = event.group_id, event.user_id
        if not check_group_allow(event.group_id):
            await matcher.finish(plugin_config.not_allow, at_sender=True)
        allow = await plugin_config.fuck_cd_check(event)  # CD检查是否允许
        if not allow:
            await matcher.finish(
                f"你已经榨不出来任何东西了, 请先休息{round(plugin_config.fuck_cd_time-(time.time() - plugin_config.ejaculation_cd[str(uid)]),3)}秒",
                at_sender=True,
            )
        plugin_config.ejaculation_cd.update({str(uid): time.time()})  # 记录时间
        req_user_card: str = str(event.sender.card or event.sender.nickname)
        prep_list = await bot.get_group_member_list(group_id=gid)
        return uid, req_user_card, args[0], prep_list
        
    @staticmethod
    async def yinpa_member_handle(
        prep_list: list,
        req_user_card: str,
        matcher: Matcher,
        event: GroupMessageEvent,
        random_nn: float  # 添加 random_nn 参数
    ) -> str:
        prep_list = [prep.get("user_id", 123456) for prep in prep_list]  # 群友列表
        target = await plugin_config.get_at(event)  # 获取消息有没有at
        uid = event.user_id  # 获取当前用户ID

        if target == "寄":  # 没有@对象
            # 随机抽取幸运成员
            prep_list = [user for user in prep_list if str(user) not in plugin_config.ban_id_set]  # 排除QQ号列表中的用户
            if not prep_list:  # 如果排除后没有有效用户
                prep_list = [user for user in prep_list if str(user) in plugin_config.ban_id_set]  # 从排除的用户中抽取

            if uid in prep_list:
                prep_list.remove(uid)  # 移除当前用户

            lucky_user = choice(prep_list)
            jj_length = get_jj_length(int(uid))

            if jj_length > 5:
                await matcher.send(f"现在咱将随机抽取一位幸运群友\n送给{req_user_card}色色！")
            elif 5 >= jj_length > 0:
                if random_nn < 0.5:  # 50%概率
                    await matcher.send(f"{plugin_config.botname}发现你是xnn~现在咱将{req_user_card}\n送给随机一位幸运群友色色！")
                else:
                    await matcher.send(f"现在咱将随机抽取一位幸运群友\n送给{req_user_card}色色！")
            else:
                await matcher.send(f"唔...你透不了哦~\n现在咱将{req_user_card}\n送给随机一位幸运群友色色！")
        else:  # 有@对象
            lucky_user = target

        return lucky_user

    @staticmethod
    async def yinpa_owner_handle(
        uid: int,
        prep_list: list,
        req_user_card: str,
        matcher: Matcher,
        random_nn: float  # 添加 random_nn 参数
    ) -> str:
        lucky_user: str = next(
            (prep["user_id"] for prep in prep_list if prep["role"] == "owner"),
            str(uid),
        )
        if int(lucky_user) == uid:  # 如果群主是自己
            del plugin_config.ejaculation_cd[str(uid)]
            await matcher.finish("你透你自己?")

        jj_length = get_jj_length(uid)
        if jj_length <= 0:
            await matcher.send(f"唔...你透不了哦~\n现在咱将{req_user_card}\n送给群主色色！")
        elif 5 >= jj_length > 0 and random_nn < 0.5:
            await matcher.send(f"{plugin_config.botname}发现你是xnn~现在咱将{req_user_card}\n送给群主色色！")
        else:
            await matcher.send(f"现在咱将把群主\n送给{req_user_card}色色！")

        return lucky_user

    @staticmethod
    async def yinpa_admin_handle(
        uid: int,
        prep_list: list,
        req_user_card: str,
        matcher: Matcher,
        random_nn: float  # 添加 random_nn 参数
    ) -> str:
        admin_id: list = [
            prep["user_id"] for prep in prep_list if prep["role"] == "admin" and str(prep["user_id"]) not in plugin_config.ban_id_set
        ]
        if not admin_id:  # 如果排除后没有有效用户
                admin_id: list = [
            prep["user_id"] for prep in prep_list if prep["role"] == "admin" and str(prep["user_id"]) in plugin_config.ban_id_set
        ]  # 从排除的用户中抽取
        
        if uid in admin_id:  # 如果自己是管理的话， 移除自己
            admin_id.remove(uid)
        if not admin_id:  # 如果没有管理的话, del cd信息， 然后finish
            del plugin_config.ejaculation_cd[str(uid)]
            await matcher.finish("喵喵喵? 找不到群管理!")

        lucky_user: str = choice(admin_id)  # random抽取一个管理
        jj_length = get_jj_length(uid)

        if jj_length <= 0:
            await matcher.send(f"唔...你透不了哦~\n现在咱将{req_user_card}\n送给随机一位管理色色！")
        elif 5 >= jj_length > 0 and random_nn < 0.5:
            await matcher.send(f"{plugin_config.botname}发现你是xnn~现在咱将{req_user_card}\n送给随机一位管理色色！")
        else:
            await matcher.send(f"现在咱将随机抽取一位幸运管理\n送给{req_user_card}色色！")

        return lucky_user

    async def yinpa_identity_handle(
        self,
        command: str,
        prep_list: list,
        req_user_card: str,
        matcher: Matcher,
        event: GroupMessageEvent,
        random_nn: float  # 添加 random_nn 参数
    ) -> str:
        uid: int = event.user_id
        if "群主" in command:  # 如果发送的命令里面含有群主， 说明在透群主
            return await self.yinpa_owner_handle(uid, prep_list, req_user_card, matcher, random_nn)
        elif "管理" in command:  # 如果发送的命令里面含有管理， 说明在透管理
            return await self.yinpa_admin_handle(uid, prep_list, req_user_card, matcher, random_nn)
        else:  # 最后是群员
            return await self.yinpa_member_handle(prep_list, req_user_card, matcher, event, random_nn)

    async def yinpa(
        self,
        bot: Bot,
        matcher: Matcher,
        event: GroupMessageEvent,
        args: Tuple = RegexGroup(),
    ) -> None:
        if not check_group_allow(event.group_id):
            await matcher.finish(plugin_config.not_allow, at_sender=True)
        uid, req_user_card, command, prep_list = await self.yinpa_prehandle(
            matcher=matcher, bot=bot, args=args, event=event
        )

        random_nn = random.uniform(0, 1)  # 生成一个随机数

        lucky_user: str = await self.yinpa_identity_handle(
            command=command,
            prep_list=prep_list,
            req_user_card=req_user_card,
            matcher=matcher,
            event=event,
            random_nn=random_nn  # 传递 random_nn
        )

        lucky_user_card = next(
            (
                prep["card"] or prep["nickname"]
                for prep in prep_list
                if prep["user_id"] == int(lucky_user)
            ),
            "群友",
        )

        await asyncio.sleep(2)  # 休眠2秒, 更有效果
        update_activity(int(lucky_user))  # 更新活跃度
        update_activity(uid)  # 更新活跃度

        # 检查get_jj_length的返回值并确定好要发送的消息
        jj_length = get_jj_length(uid)
        if jj_length <= 0 or (5 >= jj_length > 0 and random_nn < 0.5):
            # 1--100的随机数， 保留三位
            ejaculation = round(random.uniform(1, 100), 3)
            insert_ejaculation(int(uid), ejaculation)
            # 互换req_user_card与lucky_user_card
            repo_1 = f"好欸！{lucky_user_card}({lucky_user})用时{random.randint(1, 20)}秒 \n给 {req_user_card}({uid}) 注入了{ejaculation}毫升的脱氧核糖核酸, 当日总注入量为：{get_today_ejaculation_data(int(uid))}毫升\n"
        else:
            # 1--100的随机数， 保留三位
            ejaculation = round(random.uniform(1, 100), 3)
            insert_ejaculation(int(lucky_user), ejaculation)
            repo_1 = f"好欸！{req_user_card}({uid})用时{random.randint(1, 20)}秒 \n给 {lucky_user_card}({lucky_user}) 注入了{ejaculation}毫升的脱氧核糖核酸, 当日总注入量为：{get_today_ejaculation_data(int(lucky_user))}毫升\n"

        await matcher.send(
            repo_1
            + MessageSegment.image(f"https://q1.qlogo.cn/g?b=qq&nk={lucky_user}&s=640")
        )  # 结束

    @staticmethod
    async def open_module(
        matcher: Matcher, event: GroupMessageEvent, args: Tuple = RegexGroup()
    ) -> None:
        """开关"""
        gid: int = event.group_id
        command: str = args[0]
        if "开启" in command or "开始" in command:
            set_group_allow(gid, True)
            await matcher.finish("功能已开启喵")
        elif "禁止" in command or "关闭" in command:
            set_group_allow(gid, False)
            await matcher.finish("功能已禁用喵")

    @staticmethod
    async def query_injection(
        matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()
    ) -> None:
        """查询某人的注入量"""
        if not check_group_allow(event.group_id):
            await matcher.finish(plugin_config.not_allow, at_sender=True)
        target = args.extract_plain_text()  # 获取命令参数
        user_id: str = event.get_user_id()
        # 判断带不带at
        [object_id, replay1] = (
            [await plugin_config.get_at(event), "该用户"]
            if await plugin_config.get_at(event) != "寄"
            else [user_id, "您"]
        )
        #  获取用户的所有注入数据
        data: List[Dict] = get_ejaculation_data(int(object_id))
        ejaculation = 0  # 先初始化0
        if "历史" in target or "全部" in target:
            if not data:
                await matcher.finish(f"{replay1}历史总被注射量为0ml")
            inject_data = {}
            for item in data:  # 遍历所有的日期
                temp: float = item["volume"]  # 获取注入量
                ejaculation += temp  # 注入量求和
                date: str = item["date"]  # 获取日期
                inject_data[date] = temp
            if len(inject_data) < 2:
                await matcher.finish(f"{replay1}历史总被注射量为{ejaculation}ml")

            await matcher.finish(
                MessageSegment.text(f"{replay1}历史总被注射量为{ejaculation}ml")
                + MessageSegment.image(
                    await draw_bar_chart.draw_line_chart(inject_data)
                )
            )
        else:
            ejaculation: float = get_today_ejaculation_data(int(object_id))
            await matcher.finish(f"{replay1}当日总被注射量为{ejaculation}ml")

    @staticmethod
    async def yinpa_introduce(matcher: Matcher) -> None:
        """输出用法"""
        usage_text = plugin_config.plugin_usage()
        await matcher.send(MessageSegment.text(usage_text))


impart = Impart()
