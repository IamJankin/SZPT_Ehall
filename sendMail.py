# -*- coding:utf-8 -*-
# smtplib 用于邮件的发信动作
import smtplib
# email 用于构建邮件内容
from email.mime.text import MIMEText
# 用于构建邮件头
from email.header import Header
# 读取配置文件
import configparser
import time,os

#configparser初始化
dirname = os.path.split(os.path.realpath(__file__))[0]
config = configparser.ConfigParser()
config.read(dirname + "/config.ini", encoding="utf-8")

def sendMail(subject,info):
    now_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    if config.getboolean("mail","email_enable") == True:
        # 发信方的信息：发信邮箱，QQ 邮箱授权码
        from_addr = config.get("mail", "email_sender")
        password = config.get("mail", "email_sender_pwd")

        # 收信方邮箱
        to_addr = config.get("mail", "email_recipient")

        # 发信服务器
        smtp_server = config.get("mail", "email_host")

        # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
        msg = MIMEText('温馨提示： '+info+'!\n\n当前时间：'+now_time, 'plain', 'utf-8')

        # 邮件头信息
        msg['From'] = Header(from_addr)
        msg['To'] = Header(to_addr)
        msg['Subject'] = Header(subject)

        # 开启发信服务，这里使用的是加密传输
        server = smtplib.SMTP_SSL(smtp_server)
        server.connect(smtp_server, 465)
        # 登录发信邮箱
        server.login(from_addr, password)
        # 发送邮件
        server.sendmail(from_addr, to_addr, msg.as_string())
        # 关闭服务器
        server.quit()