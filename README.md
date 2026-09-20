# Slime 软件库

自托管应用库。前台 + 后台 + Android 客户端。

## 文件结构
- app.py                后端 API
- templates/store.html  前台页面
- templates/admin.html  后台管理
- static/slime.css      样式
- static/js/extras.js   附加功能
- static/uploads/       上传图片

## 后台入口
https://slimerjk.bot.cd/admin
密码 admin123

## 服务器
IP: 23.141.172.30
重启: systemctl restart appstore

## 更新流程
1. GitHub 网页改 → Commit
2. 服务器: cd /opt/appstore && git pull
3. systemctl restart appstore

## 关键函数

### app.py
- /api/config   读写所有配置
- /api/apps     应用增删改查
- /api/upload   上传图片
- /api/client-version  更新推送
- /admin/login  后台登录

### store.html (前台)
- loadConfig()          读配置渲染首页
- renderToolsContent()  渲染工具卡片
- loadApps()            渲染软件列表
- openTool()            点工具卡片
- checkAppUpdate()      APP更新弹窗
- applyTheme()          切主题

### admin.html (后台)
- saveHome/saveAppsInfo/saveToolsInfo  保存基础信息
- saveSoftwareTabs/saveToolsTabs       保存标签
- saveItem()                           保存单张卡片
- saveClientVersion()                  更新推送
- saveSpeed()                          动效速度
- loadConfig/loadApps/loadUsers        加载数据

## 配置字段 (config表)
home_title, apps_title, tools_title, my_title,
notice_text, share_link, home_banners, notice_cards,
software_tabs, tools_tabs, my_page, bg_image,
notice_speed, banner_speed,
client_version_name, client_update_url, client_update_notes, client_force_update

## 清理历史
2026-09-20: 删除所有遮罩overlay相关代码
