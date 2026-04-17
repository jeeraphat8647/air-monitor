from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import csv
import os
import re
import datetime
import time

# ================= CONFIG =================
URL = "http://182.52.103.224/"

BASE_DIR = os.getcwd()  # ใช้ path ของ server (GitHub)
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

# ================= LOAD SAVED =================
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

# ================= GET DATA =================
def get_data(driver):

    popup = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "leaflet-popup-content"))
    )

    text = popup.text

    station = text.split("\n")[0]

    # ✅ FIX REGEX (ตัวที่ error คุณ)
    datetime_match = re.search(
        r"อัพเดทข้อมูลเวลา\s*(.+?\d{2}:\d{2})", text
    )

    date = ""
    time_data = ""

    if datetime_match:
        dt_text = datetime_match.group(1)
        parts = dt_text.rsplit(" ", 1)

        date = parts[0]
        time_data = parts[1]

    benzene_match = re.search(r"เบนซีน\s*([\d\.]+)", text)
    butadiene_match = re.search(r"1,3-บิวทาไดอีน\s*([\d\.]+)", text)

    benzene = float(benzene_match.group(1)) if benzene_match else None
    butadiene = float(butadiene_match.group(1)) if butadiene_match else None

    return station, date, time_data, benzene, butadiene

# ================= DRIVER =================
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    return driver

# ================= MAIN =================
def main():

    file_exists = os.path.isfile(CSV_PATH)

    csv_file = open(CSV_PATH, "a", newline="", encoding="utf-8-sig")
    writer = csv.writer(csv_file)

    if not file_exists:
        writer.writerow(["station", "date", "time", "benzene", "butadiene"])

    saved_records = get_saved_records()

    write_log(f"📌 Loaded {len(saved_records)} records")

    driver = None

    try:
        driver = create_driver()
        driver.get(URL)

        wait = WebDriverWait(driver, 20)

        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "leaflet-marker-icon"))
        )

        markers = driver.find_elements(By.CLASS_NAME, "leaflet-marker-icon")

        success = 0

        for i in range(len(markers)):

            try:
                markers = driver.find_elements(By.CLASS_NAME, "leaflet-marker-icon")
                marker = markers[i]

                driver.execute_script("arguments[0].click();", marker)
                time.sleep(1)

                station, date, time_data, benzene, butadiene = get_data(driver)

                key = f"{station}_{date}_{time_data}"

                if key in saved_records:
                    write_log(f"⏩ Skip: {station}")
                    continue

                if benzene is None and butadiene is None:
                    write_log(f"⚠️ No data: {station}")
                    continue

                writer.writerow([station, date, time_data, benzene, butadiene])
                csv_file.flush()

                saved_records.add(key)
                success += 1

                write_log(f"✅ {station} | BZ={benzene} | BD={butadiene}")

            except Exception as e:
                write_log(f"❌ Marker error: {e}")

        write_log(f"🎯 Done | Saved {success} stations")

    except Exception as e:
        write_log(f"❌ MAIN ERROR: {e}")

    finally:
        csv_file.close()
        if driver:
            driver.quit()

        write_log("🛑 END")

# ================= ENTRY =================
if __name__ == "__main__":
    write_log("🚀 START SERVICE")

    try:
        main()
    except Exception as e:
        write_log(f"❌ ERROR: {e}")
