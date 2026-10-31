# crawl_messages.py
import json
import os
import time
import requests

import env
BASE_URL      = env.url
CHAT_TYPE     = env.target_type
PAGE_SIZE     = env.size
SLEEP_SECONDS = env.space
TOKEN         = env.token
CHAT_ID       = env.target
OUTPUT_DIR    = env.raw_dir

os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_page(message_id=None, before=PAGE_SIZE):
    params = {
        "token": TOKEN,
        "chat-id": CHAT_ID,
        "chat-type": CHAT_TYPE,
        "before": before,
    }
    if message_id:
        params["message-id"] = message_id

    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 1:
        raise RuntimeError(f"接口返回错误: {data}")

    return data["data"]["list"]


def save_page(page_no, messages):
    """把一页原始响应写成日志文件，先写临时文件再改名，避免中断产生半截文件"""
    path = os.path.join(OUTPUT_DIR, f"page_{page_no:05d}.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    return path


def main():
    # ---------- 第一轮：取最新一页 ----------
    print(">> 获取最新消息...")
    latest = fetch_page(message_id=None, before=PAGE_SIZE)
    if not latest:
        print("没有消息")
        return

    save_page(1, latest)
    print(f"   第 1 页：{len(latest)} 条 -> 已保存")

    # 按 sendTime 找本页最老的消息作为下一轮锚点
    oldest = min(latest, key=lambda x: x.get("sendTime", 0))
    oldest_id = oldest["msgId"]

    # ---------- 往回轮询 ----------
    page_no = 1
    while True:
        page_no += 1
        time.sleep(SLEEP_SECONDS)

        print(f">> 第 {page_no} 页，锚点 message-id={oldest_id}...")
        page = fetch_page(message_id=oldest_id, before=PAGE_SIZE)

        # 返回 "锚点前 N 条 + 锚点本身"
        # 除锚点外若没有其他消息，说明到头了
        others = [m for m in page if m["msgId"] != oldest_id]
        if not others:
            print(">> 已到达最早消息，结束。")
            break

        save_page(page_no, page)
        print(f"   第 {page_no} 页：{len(page)} 条（含锚点）-> 已保存")

        # 更新锚点为本页最老的消息
        oldest = min(page, key=lambda x: x.get("sendTime", 0))
        oldest_id = oldest["msgId"]

        # 安全阀：本页只有锚点 1 条
        if len(page) <= 1:
            print(">> 返回条数不足，结束。")
            break

    print(f">> 完成！共 {page_no} 页，原始数据在 {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()