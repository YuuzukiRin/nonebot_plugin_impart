<div align="center">
  <!-- 
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  -->
  <a href="https://v2.nonebot.dev/store"><img src="./docs/NoneBotPlugin.svg" width="300" alt="logo"></a>
</div>

<div align="center">
  
# nonebot-plugin-impart

_✨ NoneBot2 银趴插件 Plus ✨_

<a href="./LICENSE">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
</div>

## 📖 介绍

nonebot-plugin-impart 是基于项目 [Special-Week/nonebot_plugin_impact](https://github.com/Special-Week/nonebot_plugin_impact) 的NoneBot2 ~~银趴~~插件, 增添了更多 ~~让群友眼前一亮的实用~~ 功能。

- 2024.11.7 更新: 修复排行榜结果显示异常

### 增加功能

- [x]  添加pk胜率, 初始胜率为50%, pk后胜方胜率-1%,败方胜率+1%
- [x]  添加 ✨登神挑战✨ 功能, 当检测到用户newnew长度超过25cm自动触发
- [x]  添加查询检测功能, 当检测到用户用户newnew长度低于5cm判定为xnn, 当检测到长度低于0判定为女孩子
- [x]  将newnew长度与"透群友"模块联动, 添加🎉反透🎉功能, 当xnn执行"透群友"指令时有50%的概率被对方反透, newnew长度低于0必被反透
- [x]  添加白名单功能, 执行"透群友"指令时自动过滤白名单列表用户
- [x]  添加对原插件数据库支持
### 功能介绍

- 对pk模块进行~~魔改~~功能添加, 增添胜率保证平衡性, 新增 ✨登神挑战✨, 当检测到用户newnew长度因任意原因(pk/打胶/嗦与被嗦)超过25cm触发挑战, 挑战状态下挑战者的获胜概率变为当前的80%, 且无法使用"打胶"与"嗦"指令(也无法被"嗦"), 只允许通过pk增加newnew长度, 当用户newnew长度因任意原因超过30cm则完成挑战(极小概率), ~~并获得🎊“牛々の神”🎊称号~~, 获胜概率变为当前125%, 重新开放“打胶”与“嗦”指令; 当用户newnew长度因任意原因跌出25cm则挑战失败, 当用户newnew长度在此基础上-5cm, 获胜概率变为当前125%, 重新开放“打胶”与“嗦”指令。
- 添加白名单功能, 在 nonebot2 项目的`.env`文件中设置`BAN_ID_LIST`, 需要注意, 如果群里中全为白名单用户~~一般不会~~则此功能失效, 当群主/管理在白名单中, 且(管理)只有一人的情况下, 执行"透群主/管理"指令时白名单也会失效。
## 💿 安装

<details open>
<summary>直接下载</summary> 
下载文件，将nonebot_plugin_impart文件夹放入您的nonebot2插件目录内(通常位于 : 你的插件根目录\src\plugins)
</details>

<details open>
<summary>使用 nb-cli 安装</summary> 
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-impart

</details>

<details>
<summary>使用包管理器安装</summary> 
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary> 

    pip install nonebot-plugin-impart

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_impart"]

</details>

## 🖇️ 迁移原插件数据库
如果你先前使用 [nonebot_plugin_impact](https://github.com/Special-Week/nonebot_plugin_impact) , 并想要迁移数据  
找到你的原插件数据库(通常位于 : 你的项目目录\data\impact\impact.db)  
将impact.db重命名为impart.db  
在你的项目目录下使用 `nb localstore` 命令来检查数据存储路径Data Dir: \nonebot2  
将impart.db放入\nonebot2\nonebot_plugin_impart文件夹中即可

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| DJ_CD_TIME | 否 | 300 | 打胶的CD  |
| PK_CD_TIME | 否 | 60 | pk的CD |
| SUO_CD_TIME | 否 | 300 | 嗦牛子的CD |
| FUCK_CD_TIME | 否 | 360 | 透群友的CD |
| ISALIVE | 否 | False | 不活跃惩罚 |
| BAN_ID_LIST | 否 | 123456, 654321 | 透群友白名单 |
## 🎉 使用
使用 `银趴帮助/impart help` 指令获取指令表
### 指令表

| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 开启银趴/禁止银趴 | 管理 | 否 | 群聊 | 开启或者关闭群银趴 |
| <日/透><群友/管理/群主> | 群员 | 否 | 群聊 | 使用<透群友>时可@指定用户 |
| pk/对决 | 群员 | 否 | 群聊 | 通过random实现pk |
| 打胶/开导 | 群员 | 否 | 群聊 | 增加自己长度 |
| 嗦牛子/嗦 | 群员 | 否 | 群聊 | 增加@用户长度(若未@则为自己) |
| 查询 | 群员 | 否 | 群聊 | 查询@用户长度(若未@则为自己) |
| jj排行榜/jjrank | 群员 | 否 | 群聊 | 输出倒数五位/前五位/自己的排名 |
| 注入查询/摄入查询 | 群员 | 否 | 群聊 | 查询@用户被透注入的量(后接<历史/全部>可查看总被摄入的量)(若未@则为自己) |
### 效果图

<details>
<summary>展开</summary>

</details>

## ✨ 特别感谢
- [Special-Week/nonebot_plugin_impact](https://github.com/Special-Week/nonebot_plugin_impact) 提供的灵感与代码支持
