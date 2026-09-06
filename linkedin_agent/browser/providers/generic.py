from linkedin_agent.browser.application_form import (
    inspect_form,
)

from linkedin_agent.browser.application_filler import (
    fill_application_form,
)


class GenericApplicationProvider:

    def inspect(self, page) -> list[dict]:
        return inspect_form(page)

    def fill(
        self,
        page,
        prepared_application,
    ) -> dict:

        fields = self.inspect(page)

        answers = {}

        for item in prepared_application.answers:

            if (
                item.answer is not None
                and not item.requires_user_input
            ):

                if item.normalized_key:
                    answers[
                        item.normalized_key
                    ] = item.answer

                answers[
                    item.question
                ] = item.answer

        return fill_application_form(
            page=page,
            fields=fields,
            answers=answers,
            resume_path=prepared_application.resume_path,
        )

    def detect_blocker(
        self,
        page,
    ) -> dict | None:

        page_text = page.locator(
            "body"
        ).inner_text().lower()

        blockers = {
            "captcha": [
                "captcha",
                "verify you are human",
                "i'm not a robot",
            ],

            "login_required": [
                "sign in to continue",
                "log in to continue",
            ],

            "account_creation": [
                "create an account",
                "create your account",
            ],

            "mfa": [
                "verification code",
                "two-factor",
                "authentication code",
            ],
        }

        for blocker_type, phrases in blockers.items():

            for phrase in phrases:

                if phrase in page_text:
                    return {
                        "type": blocker_type,
                        "message": phrase,
                    }

        return None