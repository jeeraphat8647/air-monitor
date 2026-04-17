def get_data(driver):

    popup = WebDriverWait(driver,10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME,"leaflet-popup-content"))
    )

    text = popup.text

    station = text.split("\n")[0]

    # ===== FIX DATE TIME (FINAL) =====
    datetime_match = re.search(from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

import csv
import os
import re
import datetime
import time

# ================= CONFIG =================
URL = "http://182.52.103.224/"

# ===== SAVE LOCAL (SERVER SAFE) =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "log")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "air_data.csv")
LOG_PATH = os.path.join(LOG_DIR, "air_log.txt")

# ================= LOG =================
def write_log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line)

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ================= LOAD SAVED RECORDS =================
def get_saved_records():

    records = set()

    if not os.path.exists(CSV_PATH):
        return records

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            key = f"{row[0]}_{row[1]}_{row[2]}"
            records.add(key)

    return records

# ================= EXTRACT DATA =================
def get_data(driver):

    popup = WebDriverWait(driver,10).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME,"leaflet-popup-content"))
    )

    text = popup.text
    station = text.split("\n")[0]

    # ===== FIX DATE TIME =====
    datetime_match = re.search(
        r"อัพเดทข้อมูลเวลา\s*(.+)", text
    )

    date = ""
    time_data = ""

    if datetime_match:
        dt_text = datetime_match.group(1)

        # ตัดวันที่ถึง 2569
        date_match = re.search(r"(.*?2569)", dt_text)
        date = date_match.group(1).strip() if date_match else ""

        # ดึงเวลา (0830 หรือ 08:30)
        time_match = re.search(r"2569\s*(\d{4}|\d{2}:\d{2})", dt_text)

        if time_match:
            time_data = time_match.group(1)

            if re.fullmatch(r"\d{4}", time_data):
                time_data = time_data[:2] + ":" + time_data[2:]

    # ===== VALUE =====
    benzene_match = re.search(r"เบนซีน\s*([\d\.]+)", text)
    butadiene_match = re.search(r"1,3-บิวทาไดอีน\s*([\d\.]+)", text)

    benzene = float(benzene_match.group(1)) if benzene_match else None
    butadiene = float(butadiene_match.group(1)) if butadiene_match else None

    return station, date, time_data, benzene, butadiene

# ================= DRIVER =================
def create_driver():

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.set_window_size(1920,1080)
    return driver

# ================= MAIN =================
def main():

    file_exists = os.path.isfile(CSV_PATH)

    csv_file = open(CSV_PATH,"a",newline="",encoding="utf-8-sig")
    writer = csv.writer(csv_file)

    if not file_exists:
        writer.writerow(["station","date","time","benzene","butadiene"])

    saved_records = get_saved_records()

    write_log(f"📌 Loaded {len(saved_records)} records")

    driver = None

    try:

        driver = create_driver()
        driver.get(URL)

        wait = WebDriverWait(driver,20)

        wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME,"leaflet-marker-icon"))
        )

        markers = driver.find_elements(By.CLASS_NAME,"leaflet-marker-icon")

        success_count = 0

        for i in range(len(markers)):

            try:
                markers = driver.find_elements(By.CLASS_NAME,"leaflet-marker-icon")
                marker = markers[i]

                driver.execute_script("arguments[0].click();", marker)
                time.sleep(1)

                station,date,time_data,benzene,butadiene = get_data(driver)

                current_key = f"{station}_{date}_{time_data}"

                if current_key in saved_records:
                    write_log(f"⏩ Skip: {station}")
                    continue

                if benzene is None and butadiene is None:
                    write_log(f"⚠️ No data: {station}")
                    continue

                writer.writerow([
                    station,
                    date,
                    time_data,
                    benzene,
                    butadiene
                ])

                csv_file.flush()
                saved_records.add(current_key)
                success_count += 1

                write_log(f"✅ {station} | {date} {time_data}")

            except Exception as e:
                write_log(f"❌ Marker error: {e}")

        write_log(f"🎯 Saved {success_count} stations")

    except Exception as e:
        write_log(f"❌ MAIN ERROR: {e}")

    finally:
        csv_file.close()
        if driver:
            driver.quit()

# ================= RUN LOOP (24/7) =================
if __name__ == "__main__":
    write_log("🚀 START SERVICE")

    try:
        main()
    except Exception as e:
        write_log(f"❌ ERROR: {e}")


    date = ""
    time_data = ""

    if datetime_match:
        dt_text = datetime_match.group(1)

        # ✅ ตัดวันที่จนถึงปี 2569
        date_match = re.search(r"(.*?2569)", dt_text)
        date = date_match.group(1).strip() if date_match else ""

        # ✅ ดึงเวลา (รองรับ 0830 หรือ 08:30)
        time_match = re.search(r"2569\s*(\d{4}|\d{2}:\d{2})", dt_text)

        if time_match:
            time_data = time_match.group(1)

            # แปลง 0830 → 08:30
            if re.fullmatch(r"\d{4}", time_data):
                time_data = time_data[:2] + ":" + time_data[2:]

    # ===== VALUE =====
    benzene_match = re.search(r"เบนซีน\s*([\d\.]+)", text)
    butadiene_match = re.search(r"1,3-บิวทาไดอีน\s*([\d\.]+)", text)

    benzene = float(benzene_match.group(1)) if benzene_match else None
    butadiene = float(butadiene_match.group(1)) if butadiene_match else None

    return station, date, time_data, benzene, butadiene
