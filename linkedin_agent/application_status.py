from enum import StrEnum


class ApplicationStatus(StrEnum):
    EXTERNAL_APPLICATION_REQUIRED = "external_application_required"
    FORM_DETECTED = "form_detected"
    PREPARED = "prepared"
    NEEDS_USER_INPUT = "needs_user_input"
    READY_FOR_REVIEW = "ready_for_review"
    MANUAL_REQUIRED = "manual_required"
    SUBMISSION_UNVERIFIED = "submission_unverified"
    APPLIED = "applied"