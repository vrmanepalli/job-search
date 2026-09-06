from pathlib import Path
from typing import Any
from pathlib import Path

ALLOWED_RESUME_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
}

def upload_resume(
    page,
    field: dict,
    resume_path: str,
) -> dict:
    """
    Upload a resume to one detected file input.

    Does not submit the form.
    """

    label = field.get("label")
    field_id = field.get("id")
    field_name = field.get("name")

    file_path = Path(resume_path).resolve()

    if not file_path.exists():
        return {
            "success": False,
            "field": label,
            "error": f"Resume file does not exist: {file_path}",
        }

    if not file_path.is_file():
        return {
            "success": False,
            "field": label,
            "error": f"Resume path is not a file: {file_path}",
        }

    extension = file_path.suffix.lower()

    if extension not in ALLOWED_RESUME_EXTENSIONS:
        return {
            "success": False,
            "field": label,
            "error": (
                f"Unsupported resume format: {extension}"
            ),
        }

    locator = None

    # 1. Prefer associated label
    if label:
        candidate = page.get_by_label(
            label,
            exact=True,
        )

        if candidate.count() == 1:
            locator = candidate

    # 2. Fall back to element id
    if locator is None and field_id:
        candidate = page.locator(
            f'#{field_id}'
        )

        if candidate.count() == 1:
            locator = candidate

    # 3. Fall back to name
    if locator is None and field_name:
        candidate = page.locator(
            f'input[type="file"][name="{field_name}"]'
        )

        if candidate.count() == 1:
            locator = candidate

    if locator is None:
        return {
            "success": False,
            "field": label,
            "error": "Could not locate resume upload field",
        }

    try:
        locator.set_input_files(
            str(file_path)
        )

        return {
            "success": True,
            "field": label,
            "file": file_path.name,
            "path": str(file_path),
        }

    except Exception as e:
        return {
            "success": False,
            "field": label,
            "error": str(e),
        }

def find_matching_option(
    field: dict,
    answer: str,
) -> str | None:

    answer_lower = str(answer).strip().lower()

    options = field.get(
        "options",
        [],
    )

    # 1. Exact text/value match
    for option in options:

        text = (
            option.get("text")
            or ""
        ).strip().lower()

        value = (
            option.get("value")
            or ""
        ).strip().lower()

        if answer_lower == text:
            return option.get("value")

        if answer_lower == value:
            return option.get("value")

    # 2. Conservative text-prefix match
    matches = []

    for option in options:

        text = (
            option.get("text")
            or ""
        ).strip().lower()

        if text.startswith(answer_lower):
            matches.append(
                option.get("value")
            )

    # Only use fuzzy matching when exactly one
    # option matched.
    if len(matches) == 1:
        return matches[0]

    return None

def fill_field(
    page,
    field: dict[str, Any],
    answer: str,
    resume_path: str | None = None,
) -> dict:

    field_type = field.get("type")
    field_id = field.get("id")
    field_name = field.get("name")
    label = field.get("label")

    locator = None

    if label:
        candidate = page.get_by_label(
            label,
            exact=True,
        )

        if candidate.count() == 1:
            locator = candidate

    if locator is None and field_id:
        locator = page.locator(
            f'#{field_id}'
        )

    if locator is None and field_name:
        locator = page.locator(
            f'[name="{field_name}"]'
        )

    if locator is None or locator.count() == 0:
        return {
            "success": False,
            "field": label or field_name,
            "error": "Could not locate field",
        }

    try:

        if field_type in (
            "text",
            "email",
            "tel",
            "number",
            "url",
        ):
            locator.fill(
                str(answer)
            )

        elif field_type == "textarea":
            locator.fill(
                str(answer)
            )

        elif field_type == "select":

            option_value = find_matching_option(
                field,
                str(answer),
            )

            if option_value is None:
                return {
                    "success": False,
                    "field": label,
                    "error": (
                        f"No matching dropdown option "
                        f"for answer: {answer}"
                    ),
                    "available_options": field.get(
                        "options",
                        [],
                    ),
                }

            locator.select_option(
                value=option_value
            )

        elif field_type == "checkbox":

            desired = str(answer).lower() in (
                "true",
                "yes",
                "1",
                "checked",
            )

            locator.set_checked(
                desired
            )

        elif field_type == "radio":
            locator.check()

        elif field_type == "file":

            if not resume_path:
                return {
                    "success": False,
                    "field": label,
                    "error": "No resume path provided",
                }

            return upload_resume(
                page=page,
                field=field,
                resume_path=resume_path,
            )

        else:
            return {
                "success": False,
                "field": label,
                "error": (
                    f"Unsupported field type: "
                    f"{field_type}"
                ),
            }

        return {
            "success": True,
            "field": label or field_name,
            "type": field_type,
            "answer": str(answer),
        }

    except Exception as e:
        return {
            "success": False,
            "field": label or field_name,
            "type": field_type,
            "error": str(e),
        }

def fill_application_form(
    page,
    fields: list[dict],
    answers: dict[str, str],
    resume_path: str | None = None,
) -> dict:
    """
    Fill all fields for which we have answers.

    Does NOT submit.
    """

    results = []

    missing = []

    for field in fields:

        key = field.get(
            "normalized_key"
        )

        label = field.get(
            "label"
        )

        field_type = field.get(
            "type"
        )

        # File upload is handled separately
        if field_type == "file":

            result = fill_field(
                page=page,
                field=field,
                answer="",
                resume_path=resume_path,
            )

            results.append(result)

            continue

        # Try normalized key first
        answer = None

        if key and key in answers:
            answer = answers[key]

        # Optional fallback: exact label
        elif label and label in answers:
            answer = answers[label]

        if answer is None:

            if field.get("required"):
                missing.append(
                    label
                    or field.get("name")
                    or "Unknown field"
                )

            continue

        result = fill_field(
            page=page,
            field=field,
            answer=str(answer),
            resume_path=resume_path,
        )

        results.append(result)

    return {
        "success": (
            len(missing) == 0
            and all(
                result["success"]
                for result in results
            )
        ),
        "results": results,
        "missing_required_fields": missing,
    }
