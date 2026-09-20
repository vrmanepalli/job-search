from __future__ import annotations

from typing import Any

from linkedin_agent.browser.providers.base import (
    ApplicationProvider,
)

from linkedin_agent.browser.application_filler import (
    fill_application_form,
)

from linkedin_agent.application_answer_service import (
    build_verified_answer_map,
)

class ICIMSApplicationProvider(ApplicationProvider):

    name = "icims"


    def get_active_context(self, page):
        """
        Return the page or iframe containing
        the actual iCIMS form controls.
        """

        # Main page first
        main_count = page.locator(
            "input, textarea, select"
        ).count()

        if main_count > 0:
            return page

        # Then inspect child frames
        for frame in page.frames:

            if frame == page.main_frame:
                continue

            try:
                count = frame.locator(
                    "input, textarea, select"
                ).count()

                if count > 0:
                    print(
                        "Using iCIMS frame:",
                        frame.url,
                    )
                    return frame

            except Exception:
                continue

        return page


    def _find_label(
        self,
        page,
        context,
        element,
    ) -> str | None:

        element_id = element.get_attribute(
            "id"
        )

        if element_id:

            label = context.locator(
                f'label[for="{element_id}"]'
            )

            if label.count() > 0:

                text = (
                    label.first
                    .inner_text()
                    .strip()
                )

                if text:
                    return text

        aria = element.get_attribute(
            "aria-label"
        )

        if aria:
            return aria.strip()

        placeholder = (
            element.get_attribute(
                "placeholder"
            )
        )

        if placeholder:
            return placeholder.strip()

        return None


    def inspect(
        self,
        page,
    ) -> list[dict]:

        fields = []

        context = self.get_active_context(page)

        inputs = context.locator(
            "input, textarea, select"
        )

        count = inputs.count()

        print(
            "iCIMS field count:",
            count
        )

        for i in range(count):

            element = inputs.nth(i)
            try:

                tag = element.evaluate(
                    "el => el.tagName.toLowerCase()"
                )

                field_type = (
                    element.get_attribute("type")
                    or tag
                )

                name = element.get_attribute(
                    "name"
                )

                element_id = element.get_attribute(
                    "id"
                )

                placeholder = (
                    element.get_attribute(
                        "placeholder"
                    )
                )

                aria_label = (
                    element.get_attribute(
                        "aria-label"
                    )
                )

                label = self._find_label(
                    page,
                    context,
                    element,
                )

                fields.append({
                    "index": i,
                    "tag": tag,
                    "type": field_type,
                    "name": name,
                    "id": element_id,
                    "placeholder": placeholder,
                    "aria_label": aria_label,
                    "label": label,
                })

            except Exception as exc:

                print(
                    f"Could not inspect field {i}:",
                    exc,
                )

        return fields

    def detect_page_state(self, page) -> str:
        context = self.get_active_context(page)

        url = page.url.lower()
        title = page.title().lower()

        try:
            body_text = (
                context.locator("body")
                .inner_text()
                .lower()
            )
        except Exception:
            body_text = ""

        if (
            "captcha" in body_text
            or "verify you are human" in body_text
            or "human verification" in body_text
        ):
            return "captcha"

        if (
            "verification code" in body_text
            or "two-factor" in body_text
            or "authentication code" in body_text
        ):
            return "mfa"

        if (
            "create account" in body_text
            or "create profile" in body_text
            or "register" in body_text
        ):
            return "account_creation"

        file_inputs = context.locator(
            'input[type="file"]'
        ).count()

        form_fields = context.locator(
            "input, textarea, select"
        ).count()

        if file_inputs > 0:
            return "application_form"

        if form_fields > 2:
            return "application_form"

        if (
            "/login" in url
            or "login" in title
            or "sign in" in body_text
        ):
            return "login"

        if "apply" in body_text:
            return "job_page"

        return "unknown"


    def detect_blocker(
        self,
        page,
    ) -> dict | None:

        state = self.detect_page_state(
            page
        )

        blockers = {
            "captcha": (
                "CAPTCHA or human verification detected."
            ),

            "mfa": (
                "Multi-factor authentication detected."
            ),

            "login": (
                "Candidate login is required."
            ),

            "account_creation": (
                "Candidate account creation is required."
            ),
        }

        message = blockers.get(
            state
        )

        if not message:
            return None

        return {
            "type": state,
            "message": message,
            "provider": "icims",
        }

    def fill(
        self,
        page,
        prepared_application,
    ) -> dict:

        context = self.get_active_context(page)

        fields = self.inspect(page)

        answers = build_verified_answer_map(
            prepared_application
        )

        return fill_application_form(
            page=context,
            fields=fields,
            answers=answers,
            resume_path=prepared_application.resume_path,
        )

    def verify_submission(self, page) -> bool:

        context = self.get_active_context(page)

        try:
            body_text = (
                context
                .locator("body")
                .inner_text()
                .lower()
            )
        except Exception:
            return False

        confirmation_phrases = [
            "application submitted",
            "application received",
            "thank you for applying",
            "thank you for your application",
        ]

        return any(
            phrase in body_text
            for phrase in confirmation_phrases
        )

    def submit(self, page) -> dict:

        context = self.get_active_context(page)

        submit_selectors = [
            'button:has-text("Submit")',
            'input[type="submit"]',
            'button[type="submit"]',
        ]

        for selector in submit_selectors:

            locator = context.locator(selector)

            if locator.count() == 0:
                continue

            button = locator.first

            try:
                if not button.is_visible():
                    continue

                text = (
                    button.inner_text()
                    if button.evaluate(
                        "(el) => el.tagName.toLowerCase() === 'button'"
                    )
                    else button.get_attribute("value")
                )

                print(
                    f"Found submit candidate: "
                    f"{text!r}"
                )

                button.click()

                page.wait_for_timeout(2000)

                return {
                    "success": True,
                    "clicked": True,
                    "button_text": text,
                }

            except Exception as exc:
                return {
                    "success": False,
                    "clicked": False,
                    "error": str(exc),
                }

        return {
            "success": False,
            "clicked": False,
            "error": "Submit button not found",
        }