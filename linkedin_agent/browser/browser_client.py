from pathlib import Path

from playwright.sync_api import (
    sync_playwright,
)


class BrowserClient:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()

        profile_dir = Path(
            "playwright_profile"
        ).resolve()

        profile_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.context = (
            self.playwright.chromium
            .launch_persistent_context(
                user_data_dir=str(
                    profile_dir
                ),

                headless=False,

                viewport={
                    "width": 1400,
                    "height": 900,
                },
            )
        )

        if self.context.pages:

            self.page = (
                self.context.pages[0]
            )

        else:

            self.page = (
                self.context.new_page()
            )

        return self.page

    def open(self, url: str):
        if not self.page:
            self.start()

        self.page.goto(url)

    def close(self):
        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()