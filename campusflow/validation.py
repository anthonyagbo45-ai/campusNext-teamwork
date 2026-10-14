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