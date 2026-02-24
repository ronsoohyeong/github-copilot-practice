from __future__ import annotations

from pathlib import Path
from time import sleep

import requests
from playwright.sync_api import sync_playwright


API_BASE = "http://127.0.0.1:8000"
UI_URL = "http://127.0.0.1:8501"
OUTPUT_DIR = Path("captures")


def build_body_text(target_length: int = 200) -> str:
    text = ""
    while len(text) < target_length:
        text += "." * 10
        text += str(len(text))
    return text[:target_length]


def api_get_list() -> list[list[int | str]]:
    response = requests.get(f"{API_BASE}/articles", timeout=5)
    response.raise_for_status()
    return response.json()


def api_post_article(title: str, body: str, created_time: str) -> None:
    response = requests.post(
        f"{API_BASE}/articles",
        json={"title": title, "body": body, "time": created_time},
        timeout=5,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("success"):
        raise RuntimeError(f"Post failed for title={title}")


def api_delete_article(article_id: int) -> None:
    response = requests.delete(f"{API_BASE}/articles/{article_id}", timeout=5)
    response.raise_for_status()
    result = response.json()
    if not result.get("success"):
        raise RuntimeError(f"Delete failed for id={article_id}")


def clear_all_articles() -> None:
    while True:
        current = api_get_list()
        if not current:
            return
        for article_id, _, _ in current:
            api_delete_article(int(article_id))


def capture(page, file_name: str) -> None:
    page.goto(UI_URL, wait_until="networkidle")
    sleep(0.7)
    page.screenshot(path=str(OUTPUT_DIR / file_name), full_page=True)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    requests.get(f"{API_BASE}/articles", timeout=5).raise_for_status()
    requests.get(UI_URL, timeout=5).raise_for_status()

    clear_all_articles()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1800})

        step = 1
        capture(page, f"step_{step:02d}_start.png")
        step += 1

        for n in range(1, 21):
            title = f"{n}번째 article"
            body = build_body_text(200)
            created_time = f"2026-02-24 17:{n:02d}:00"
            api_post_article(title=title, body=body, created_time=created_time)

            capture(page, f"step_{step:02d}_post_{n:02d}.png")
            step += 1

            if n % 5 == 0:
                latest_five = api_get_list()[:5]
                middle = latest_five[2]
                middle_id = int(middle[0])
                api_delete_article(middle_id)

                capture(page, f"step_{step:02d}_delete_after_{n:02d}.png")
                step += 1

        browser.close()

    final_list = api_get_list()
    print(f"saved_screenshots={step - 1}")
    print(f"remaining_articles={len(final_list)}")
    if final_list:
        print(f"latest_article={final_list[0]}")


if __name__ == "__main__":
    main()
