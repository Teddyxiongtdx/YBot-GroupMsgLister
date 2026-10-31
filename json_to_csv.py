# json_to_csv.py
import csv
import glob
import json
import os

import env
RAW_DIR    = env.raw_dir
OUTPUT_CSV = env.output_name

fieldnames = [
    "msgId", "parentId", "senderId", "senderType", "senderNickname",
    "contentType", "content_text", "sendTime", "commandName", "commandId",
]

seen = set()
rows = []

files = sorted(glob.glob(os.path.join(RAW_DIR, "page_*.json")))
print(f">> 找到 {len(files)} 个 JSON 文件")

for fp in files:
    with open(fp, "r", encoding="utf-8") as f:
        messages = json.load(f)

    for m in messages:
        mid = m.get("msgId")
        if not mid or mid in seen:
            continue
        seen.add(mid)

        content = m.get("content") or {}
        rows.append({
            "msgId": mid,
            "parentId": m.get("parentId", ""),
            "senderId": m.get("senderId", ""),
            "senderType": m.get("senderType", ""),
            "senderNickname": m.get("senderNickname", ""),
            "contentType": m.get("contentType", ""),
            "content_text": content.get("text", ""),
            "sendTime": m.get("sendTime", ""),
            "commandName": m.get("commandName", ""),
            "commandId": m.get("commandId", ""),
        })

# 按 sendTime 升序（老的在前）
rows.sort(key=lambda r: r["sendTime"])

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f">> 完成！去重后共 {len(rows)} 条 -> {OUTPUT_CSV}")