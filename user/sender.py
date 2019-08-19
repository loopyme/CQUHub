from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import time, random
from my_project.settings import DEBUG, MAIL_PSW


class Sender:
    __tokens = {}
    __debug = DEBUG
    __mail_content = {
        "title": "CQU Hub的注册验证",
        "content": """
        您好:

            感谢您使用CQU Hub！
            为确保论坛只对重大学子开放，请确认您的学号为  {}  ，并使用验证码  {}  来完成您的注册！
            如果您并没有在CQU Hub进行注册，请忽略此邮件。

        顺颂 时祺

        CQU Hub开发组
        {}
        """,
    }
    __mail_config = {
        "host_server": "smtp.exmail.qq.com",
        "psw": MAIL_PSW,
        "sender": "cquhub-no-reply@mail.loopy.tech",
        "receiver": "{}@cqu.edu.cn",
    }

    @classmethod
    def config(cls, **kwargs):
        for key in kwargs:
            if key == "debug":
                cls.__debug = kwargs[key]
            elif key in cls.__mail_content.keys():
                cls.__mail_content[key] = kwargs[key]
            elif key in cls.__mail_config.keys():
                cls.__mail_config[key] = kwargs[key]
            else:
                raise AttributeError('"Sender" has no attribute called {}'.format(key))

    @staticmethod
    def generate_token(student_id):
        token = str(random.randint(0, 10 ** 6 - 1)).zfill(6)
        Sender.__tokens[student_id] = [token, time.time()]
        return token

    @staticmethod
    def update_token():
        for id in list(Sender.__tokens.keys()):
            if Sender.__tokens[id][1] - time.time() > 3600:
                # token expired in 6 min
                del Sender.__tokens[id]

    @staticmethod
    def check_token(student_id, input_token):
        Sender.update_token()
        return (
            student_id in Sender.__tokens.keys()
            and Sender.__tokens[student_id][0] == input_token
        )

    @staticmethod
    def send_verify_mail(student_id):
        if Sender.__debug:
            print("*" * 79 + "\n" + Sender.generate_token(student_id) + "\n" + "*" * 79)
            return

        smtp = SMTP_SSL(Sender.__mail_config["host_server"])

        smtp.set_debuglevel(0)
        smtp.ehlo(Sender.__mail_config["host_server"])
        smtp.login(Sender.__mail_config["sender"], Sender.__mail_config["psw"])

        msg = MIMEText(
            Sender.__mail_content["content"].format(
                student_id,
                Sender.generate_token(student_id),
                time.strftime("%Y-%m-%d %X", time.localtime()),
            ),
            "plain",
            "utf-8",
        )
        msg["Subject"], msg["From"], msg["To"] = (
            Header(Sender.__mail_content["title"], "utf-8"),
            Sender.__mail_config["sender"],
            Sender.__mail_config["receiver"],
        )

        smtp.sendmail(
            Sender.__mail_config["sender"],
            Sender.__mail_config["receiver"],
            msg.as_string(),
        )
        smtp.quit()
