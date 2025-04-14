import requests
import time
import smtplib
import copy
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# xxxx is the reviewer id
urls = {
    7200: "https://cmt3.research.microsoft.com/api/odata/IJCAI2025/ReviewViews(xxxx)",
    16709: "https://cmt3.research.microsoft.com/api/odata/IJCAI2025/ReviewViews(xxxx)",
    10641: "https://cmt3.research.microsoft.com/api/odata/IJCAI2025/ReviewViews(xxxx)",
    11802: "https://cmt3.research.microsoft.com/api/odata/IJCAI2025/ReviewViews(xxxx)",
}

# 初始评分状态（第一次抓到后自动初始化）
last_scores = {}

# Cookie 与 Headers
cookies = {
    ".AspNetCore.Cookies":  # cookies, replace with your own cookies
    ".ROLE": "Author",
    ".TRACK": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://cmt3.research.microsoft.com/IJCAI2025/Submission/Index",
    "Origin": "https://cmt3.research.microsoft.com"
}

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

# 邮件配置
def send_email(subject, body):
    sender = "your email"
    receiver = "your email"
    password = "your password"  # your password

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.qq.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("📧 Email sent successfully!")
    except Exception as e:
        print(f"❌ Email send failed: {e}")



# 主循环
while True:
    for rid, url in urls.items():
        try:
            response = requests.get(url, headers=headers, cookies=cookies, proxies=proxies, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for question in data.get("Questions", []):
                    if question.get("Order") == 7:
                        new_value = question.get("Answers", [{}])[0].get("Value")
                        print(f"[{rid}] {new_value}",end="")
                        if rid not in last_scores:
                            last_scores[rid] = new_value
                        elif new_value != last_scores[rid]:
                            # 发生了变化
                            old = last_scores[rid]
                            last_scores[rid] = new_value  # 更新缓存值
                            title = data.get("SubmissionTitle", "Unknown Title")
                            msg = (
                                f"🔔 Score Changed!\n\n"
                                f"Paper ID: {rid}\n"
                                f"Title: {title}\n"
                                f"Old Score: {old}\n"
                                f"New Score: {new_value}\n"
                                f"Link: {url}"
                            )
                            print(msg)
                            send_email("IJCAI2025 - Review Score Changed", msg)
                        else:
                            print(f"[{rid}] No change: {new_value}")
                        break
                print("")
            else:
                print(f"Failed to fetch {rid}, Status code: {response.status_code}")
        except Exception as e:
            print(f"[Error] {rid} -> {e}")

    # 每 3 分钟检查一次
    time.sleep(100)
