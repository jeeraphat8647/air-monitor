import re

text = "อัพเดทข้อมูลเวลา 17 เมษายน 2569 14:30"

datetime_match = re.search(
    r"อัพเดทข้อมูลเวลา\s*(.+?\d{2}:\d{2})", text
)

if datetime_match:
    dt_text = datetime_match.group(1)
    parts = dt_text.rsplit(" ", 1)

    date = parts[0]
    time_data = parts[1]

    print(date)
    print(time_data)
