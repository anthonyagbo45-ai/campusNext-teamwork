from campusflow.constants import CATEGORIES, URGENCY_LEVELS
from campusflow.errors import ValidationError


def validate_affected_users(value):
    # bool must be rejected first, because isinstance(True, int) is True
    if isinstance(value, bool):
        raise ValidationError(
            "affected users must be a whole number of 1 or more, not True/False"
        )

    # rejects 2.5, "5", None, lists, and so on
    if not isinstance(value, int):
        raise ValidationError(
            "affected users must be a whole number of 1 or more"
        )

    # rejects 0 and negative numbers
    if value < 1:
        raise ValidationError(
            "affected users must be a whole number of 1 or more"
        )

    return value


def _match_choice(value, allowed, label):
    if isinstance(value, str):
        for option in allowed:
            if value.strip().lower() == option.lower():
                return option
    raise ValidationError(
        f"Invalid {label} {value!r}. Allowed: {', '.join(allowed)}."
    )


def validate_category(value):
    return _match_choice(value, CATEGORIES, "category")


def validate_urgency(value):
    return _match_choice(value, URGENCY_LEVELS, "urgency")


def _validate_text(value, message):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(message)
    return value.strip()


def validate_title(value):
    return _validate_text(value, "Title must not be blank.")


def validate_staff_label(value):
    return _validate_text(value, "Staff member name must not be blank.")
