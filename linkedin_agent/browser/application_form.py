from typing import Any

from linkedin_agent.application_question_normalizer import (
    normalize_question,
)

def get_field_label(page, element) -> str | None:
    """
    Try to find a human-readable label for a form element.
    """

    element_id = element.get_attribute("id")

    # Preferred case:
    # <label for="phone">Phone Number</label>
    if element_id:
        label = page.locator(
            f'label[for="{element_id}"]'
        )

        if label.count() > 0:
            text = label.first.inner_text().strip()

            if text:
                return text

    # aria-label
    aria_label = element.get_attribute("aria-label")

    if aria_label:
        return aria_label.strip()

    # Placeholder fallback
    placeholder = element.get_attribute("placeholder")

    if placeholder:
        return placeholder.strip()

    # Name fallback
    name = element.get_attribute("name")

    if name:
        return name

    return None

def get_common_field_metadata(
    page,
    element,
) -> dict:

    label = get_field_label(
        page,
        element,
    )

    return {
        "label": label,
        "normalized_key": (
            normalize_question(label)
            if label
            else None
        ),
        "name": element.get_attribute("name"),
        "id": element.get_attribute("id"),
        "required": (
            element.get_attribute("required")
            is not None
        ),
        "accept": element.get_attribute(
            "accept"
        ),
    }

def inspect_form(page) -> list[dict[str, Any]]:
    """
    Inspect inputs, textareas and selects.

    This function is read-only.
    It does not fill or submit the form.
    """

    fields = []

    # ==========================================================
    # INPUTS
    # ==========================================================

    inputs = page.locator("input")

    for i in range(inputs.count()):
        element = inputs.nth(i)

        field_type = (
            element.get_attribute("type")
            or "text"
        )

        metadata = get_common_field_metadata(
                    page,
                    element,
                )

        checked = None

        if field_type in ("checkbox", "radio"):
            checked = element.is_checked()

        fields.append(
            {
                "tag": "input",
                "type": field_type,
                **metadata,
                "placeholder": element.get_attribute(
                    "placeholder"
                ),
                "value": element.get_attribute("value"),
                "checked": checked,
            }
        )

    # ==========================================================
    # TEXTAREAS
    # ==========================================================

    textareas = page.locator("textarea")

    for i in range(textareas.count()):
        element = textareas.nth(i)

        metadata = get_common_field_metadata(
            page,
            element,
        )

        try:
            current_value = element.input_value()
        except Exception:
            current_value = None

        fields.append(
            {
                "tag": "textarea",
                "type": "textarea",
                **metadata,
                "placeholder": element.get_attribute(
                    "placeholder"
                ),
                "value": element.input_value(),
                "maxlength": element.get_attribute(
                    "maxlength"
                ),
            }
        )

    # ==========================================================
    # SELECT / DROPDOWNS
    # ==========================================================

    selects = page.locator("select")

    for i in range(selects.count()):
        element = selects.nth(i)

        metadata = get_common_field_metadata(
                    page,
                    element,
                )

        # Read available options
        options = element.locator("option")

        option_values = []

        for j in range(options.count()):
            option = options.nth(j)

            option_values.append(
                {
                    "text": option.inner_text().strip(),
                    "value": option.get_attribute("value"),
                    "selected": (
                        option.get_attribute("selected")
                        is not None
                    ),
                }
            )

        try:
            current_value = element.input_value()
        except Exception:
            current_value = None

        fields.append(
            {
                "tag": "select",
                "type": "select",
                **metadata,
                "value": current_value,
                "multiple": (
                    element.get_attribute("multiple")
                    is not None
                ),
                "options": option_values,
            }
        )

    return fields