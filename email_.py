import smtplib
from email.mime.text import MIMEText
# import datetime as dt

from mechmark.config import cfg


def Send_email(to, subject, msg, cc=None, bcc=None):
    from_ = f"bot@{cfg.get('app', 'domain')}"

    send_to = []  # Yes, we really need to...
    send_to += to

    if cc:
        send_to += cc
        msg['CC'] = ', '.join(cc)

    if bcc:
        send_to += bcc
        # msg['Bcc'] = bcc # Don't add bcc to headers!

    msg = MIMEText(msg)
    msg['To'] = ", ".join(to)
    msg['From'] = from_
    msg['Subject'] = subject

    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(from_, send_to, msg.as_string())
    except Exception as e:
        print("Error sending email to {}".format(to))
        print(e)
    finally:
        s.quit()
