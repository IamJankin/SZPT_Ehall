# SZPT_Ehall
SZPT关于防疫期间学生信息每日线上填报爬虫

基于https://github.com/AtmosphereMao/SZPT_Ehall_xsjkxxbs 第一版修改



## 功能

- 一键填报
  - 自动爬取表单并填报
  - 填报状态可以发送到邮箱进行通知

- 自动填报
  - Linux配合crontab实现自动填报
  - Windows开机填报或任务计划自动填报

**注意：如果行程或相关信息有变更，一定要手动填报以更新表单。本脚本可以用来解放双手，但一定要配合防疫工作。**



## 安装

运行环境：[Python3](https://www.python.org/)

安装第三方库：`pip install -r requirements.txt`



## 使用教程

### config.ini

配置`config.ini`，配置用户名密码，邮箱，此时就可以运行了，如果需要实现自动填报，可以往下看。

```
[root@test]# python3 SZPT_Ehall.py 
[+] 登录成功
[+] 今日已经填报，填报时间：2021-01-28 10:20:21
```

配置自动填报的话，可以在`config.ini`文件中配置`time_sleep = 60`随机延时1~60秒运行。



## 自动填报

### Linux填报

配置mission_plan目录里的`linux`文件，修改相应路径及时间，添加权限并运行`linux`文件。

注：运行`linux`文件会重置crontab内容，请做好备份，或将crontab的内容写入到`linux`文件中。  



### Windows自动填报

配置mission_plan目录里的`windows.vbs`文件，修改相应路径。在Windows自带的**任务计划程序**中添加该文件，定时运行以实现自动填报。



### Windows开机填报/一键填报

Windows也可以将`windows.vbs`文件放在开机启动项里，Win10路径：`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp`

登录进去就会自动运行填报程序了，但是刚开机如果没有网络，会导致填报失败，可以将`windows.vbs`放到桌面，双击一键填报。



## **注意：如果行程有变更，一定要手动填报以更新表单。**

**如果行程或相关信息有变更，一定要手动填报以更新表单。本脚本可以用来解放双手，但一定要配合防疫工作。**

