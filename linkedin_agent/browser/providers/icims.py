from __future__ import annotations

from typing import Any


class ICIMSApplicationProvider:

    name = "icims"

    def inspect(
        self,
        page,
    ) -> list[dict[str, Any]]:

        raise NotImplementedError

    def fill(
        self,
        page,
        prepared_application,
    ) -> dict:

        raise NotImplementedError

    def detect_blocker(
        self,
        page,
    ) -> dict | None:

        raise NotImplementedError

    def verify_submission(
        self,
        page,
    ) -> bool:

        raise NotImplementedError


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
        element,
    ) -> str | None:

        element_id = element.get_attribute(
            "id"
        )

        if element_id:

            label = page.locator(
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
        url = page.url.lower()
        title = page.title().lower()

        try:
            context = self.get_active_context(page)

            form_fields = context.locator(
                "input, textarea, select"
            ).count()
            
            body_text = page.locator("body").inner_text().lower()
        except Exception:
            body_text = ""

        print("DEBUG TITLE:", title)
        print("DEBUG URL:", url)
        print("DEBUG BODY:", body_text[:1000])

        # Hard blockers / manual steps
        if (
            "captcha" in body_text
            or "verify you are human" in body_text
            or "human verification" in body_text
        ):
            return "captcha"

        if (
            "verification code" in body_text
            or "two-factor" in body_text
            or "2-factor" in body_text
        ):
            return "mfa"

        # iCIMS login page
        if (
            "/login" in url
            or "login" in title
            or "sign in" in body_text
        ):
            return "login"

        if (
            "create account" in body_text
            or "create profile" in body_text
            or "register" in body_text
        ):
            return "account_creation"

        # Application form
        file_inputs = page.locator('input[type="file"]').count()

        form_fields = page.locator(
            "input, textarea, select"
        ).count()

        if file_inputs > 0:
            return "application_form"

        if form_fields > 2:
            return "application_form"

        # Job page / apply gateway
        if (
            "apply" in body_text
            or "/jobs/" in url
        ):
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