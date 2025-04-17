import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor, as_completed

# xxxx is the reviewer id (replace it with your own reviewer ID)
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




def monitor_review_scores():
    i = 0
    last_scores = {}
    rebuttal_seen = {}

    while True:
        i += 1
        print(f"--------------------{i}--------------------")
        for rid, url in urls.items():
            try:
                response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rebuttal_found = "rebuttal" in response.text

                    for question in data.get("Questions", []):
                        if question.get("Order") == 7:
                            new_value = question.get("Answers", [{}])[0].get("Value")
                            print(f"[{rid}] {new_value}", end="")
                            if rid not in last_scores:
                                last_scores[rid] = new_value
                            elif new_value != last_scores[rid]:
                                old = last_scores[rid]
                                last_scores[rid] = new_value
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
                            elif rebuttal_found and not rebuttal_seen.get(rid, False):
                                rebuttal_seen[rid] = True
                                title = data.get("SubmissionTitle", "Unknown Title")
                                msg = (
                                    f"🔔 Rebuttal Detected!\n\n"
                                    f"Paper ID: {rid}\n"
                                    f"Title: {title}\n"
                                    f"Rebuttal found.\n"
                                    f"Link: {url}"
                                )
                                print(msg)
                                send_email("IJCAI2025 - Rebuttal Detected", msg)
                            else:
                                print(f"[{rid}] No change: {new_value}")
                            break
                    print("")
                else:
                    print(f"[{i}] Failed to fetch {rid}, Status code: {response.status_code}")
            except Exception as e:
                print(f"[{i}] [Error] {rid} -> {e}")

        time.sleep(180)



# 单个 ID 检查函数
def check_metareview_id(rid):
    url = f"https://cmt3.research.microsoft.com/api/odata/IJCAI2025/MetaReviewViews({rid})"
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=5)
        if response.status_code == 200 and "does not exist." not in response.text:
            print(f"✅ Found! MetaReview ID: {rid}")
            send_email("IJCAI2025 - MetaReview Found",
                       f"Found valid MetaReview ID: {rid}\nLink: {url}\n\nResponse:\n{response.text}")
            return True  # 找到了
        else:
            return False
    except Exception as e:
        print(f"[Error] ID {rid} -> {e}")
        return False


# 并发爆破函数
def brute_force_metareview_parallel(start=1, end=50000, batch_size=1000, max_workers=64):
    for batch_start in range(start, end, batch_size):
        batch_end = min(batch_start + batch_size, end)
        print(f"\n🚀 Scanning batch: {batch_start} - {batch_end - 1}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {executor.submit(check_metareview_id, rid): rid for rid in range(batch_start, batch_end)}

            for future in as_completed(future_to_id):
                rid = future_to_id[future]
                try:
                    if future.result():
                        print(f"🎯 Stopping early: Found valid MetaReview ID {rid}")
                        return  # 立即退出整个批次处理
                except Exception as e:
                    print(f"❌ Future exception: {e}")

        print(f"📭 Batch {batch_start}-{batch_end - 1} completed. No result found yet.")


# 主入口
if __name__ == "__main__":
    brute_force_metareview_parallel(start=1, end=50000, batch_size=1000, max_workers=64)

