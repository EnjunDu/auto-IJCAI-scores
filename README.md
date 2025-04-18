# IJCAI 2025 Review & MetaReview Monitor

## Please STAR qwq :)

This repository provides two Python scripts to help authors monitor review scores and rebuttal statuses for IJCAI 2025 submissions via CMT. It also supports brute-force searching of valid MetaReview IDs using parallel HTTP requests.

## 🚀 Features

- **Monitor Review Scores (`ijcai.py` & `parallel.py`)**
  - Tracks changes in review scores or detects rebuttal availability.
  - Sends email notifications when updates occur.
  - **`monitor_review_scores()` can also be used independently to continuously check review changes.**
  - **The ijcai.py can search the meta-ID as well, but with much lower speed, if you are using your own computer instead of a server, then ijcai.py is highly recommended.**
- **Parallel MetaReview ID Discovery (`parallel.py`)**
  - Scans potential `MetaReviewView` IDs to find valid ones.
  - Supports high-speed parallel requests with progress checkpoints.
  - Sends notifications when a valid ID is found.

------

## 🧰 Requirements

- Python 3.8+
- `requests`
- `smtplib` (built-in)
- Internet access (via proxy if required)


## ⚙️ Setup

1. **Edit Cookie and Email Configurations**
    Modify the following variables in both scripts:

   ```
   cookies = {
       ".AspNetCore.Cookies": "your_cookie_here",
       ".ROLE": "Author",
       ".TRACK": "1"
   }
   
   sender = "your_email@example.com"
   receiver = "your_email@example.com"
   password = "your_email_password"
   ```

2. **Proxy (Optional)**
    If using a local proxy (e.g., for CMT access in some regions), configure as:

   ```
   proxies = {
       "http": "http://127.0.0.1:7890",
       "https": "http://127.0.0.1:7890"
   }
   ```

------

## 📄 Usage

### 1. Monitor Review Scores

Tracks score updates and rebuttal notices for a list of paper IDs.

```
python ijcai.py
```

Or, from within another script:

```
from parallel import monitor_review_scores
monitor_review_scores()
```

> ⚠️ Replace `xxxx` in the `urls` dictionary with your actual reviewer or paper IDs.

### 2. Brute Force MetaReview IDs (Parallelized)

Find valid `MetaReviewViews(ID)` endpoints using concurrent requests:

```
python parallel.py
```

- Checkpoints are saved in `metareview_state.txt`.
- Found IDs are logged in `metareview_found.log`.

You can resume from the last checkpoint automatically. Customize scanning range and speed:

```
brute_force_metareview_parallel(end=50000, batch_size=1000, max_workers=96)
```

### 3. View Your MetaReview

If you have found your `meta-ID`, you can view your meta review using the following URL format:

```
https://cmt3.research.microsoft.com/api/odata/IJCAI2025/MetaReviewViews(meta-id)
```

Replace `meta-id` with the numeric ID you found.

------

## 📬 Email Alerts

Both scripts use SMTP to send notification emails when:

- A review score is updated
- A rebuttal becomes available
- A valid MetaReview ID is found

> Default uses `smtp.qq.com` on port 587. You can replace it with your own SMTP server.

------

## ⚠️ Disclaimer

This tool is for personal use only. Be respectful of IJCAI/CMT system usage policies. Excessive requests may lead to temporary blocks or IP bans.

------

## 📌 License

MIT License
