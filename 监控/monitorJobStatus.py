# -*- coding: utf-8 -*-
import requests
import json
import pymysql
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# MySQL数据库连接信息
HOST = 'localhost'
USER = 'root'
PASSWORD = '123456'
DB = 'bigdata_etl'
PORT = 3306

# 监控表格
TABLE_NAME = 'v2_job'

# 上次状态记录
last_state = {}

WEBHOOK_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=372def7c-1657-4ee3-bf69-0d3b44581d14'


def get_db_connection():
    return pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        db=DB,
        port=PORT,
        charset='utf8mb4'
    )


def send_wechat_message(content):
    message = {
        "msgtype": "text",  # 消息类型
        "at": {
            "isAtAll": "true"
        },
        "text": {
            "content": content  # 发送的消息内容
        }
    }

    try:
        response = requests.post(WEBHOOK_URL, data=json.dumps(message), headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            print("消息发送成功")
        else:
            print(f"发送失败，状态码: {response.status_code}, 错误信息: {response.text}")
    except Exception as e:
        print(f"发生错误: {e}")


# 监控并报警
def monitor_job_status():
    global last_state
    con = get_db_connection()
    try:
        with con.cursor() as cursor:
            # 状态检测：
            query = (
                f" SELECT job_id,job_name, is_enable, execution_state, is_push FROM {TABLE_NAME} WHERE is_delete = 0 ")
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                job_id, job_name, is_enable, execution_state, is_push = row
                key = f'{job_id}'
                # 检查是否需要发出警报
                if key in last_state:
                    last_is_enable, last_execution_state, last_is_push = last_state[key]
                    if last_is_enable != is_enable and is_enable == 0:
                        status = '已暂停'
                        # print(f"ETL告警： JobId: {job_id} , {job_name}{status}")
                        send_wechat_message(f"ETL告警： JobId: {job_id} , {job_name}{status}")

                    if last_is_push != is_push and is_push == 1:
                        # print(f"ETL告警： JobId: {job_id} ,{job_name}的信息未推送")
                        send_wechat_message(f"ETL告警： JobId: {job_id} ,{job_name}的信息未推送")

                    if last_execution_state != execution_state and execution_state == 3:
                        status = '执行异常'
                        # print(f"ETL告警： JobId: {job_id}, {job_name}{status}")
                        send_wechat_message(f"ETL告警： JobId: {job_id}, {job_name}{status}")
                last_state[key] = (is_enable, execution_state, is_push)
    finally:
        con.close()


# 监控相关
# def start_monitoring(interval=10):
#     while True:
#         monitor_job_status()
#         time.sleep(interval)  # 每10秒监控一次
#
#
# if __name__ == '__main__':
#     start_monitoring()
