def build_answer_map(
    prepared_application,
) -> dict[str, str]:

    answers = {}

    for item in prepared_application.answers:
        if (
            item.answer is None
            or item.requires_user_input
        ):
            continue

        if item.normalized_key:
            answers[
                item.normalized_key
            ] = item.answer

        answers[
            item.question
        ] = item.answer

    return answers