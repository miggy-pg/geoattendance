from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_domainonly_email(value):
    if not "g.msuiit.edu.ph" in value:
        raise ValidationError(_("Sorry, the email submitted is not a MyIIT email."))
    return value