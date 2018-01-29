from django.utils.translation import ugettext_lazy as _

MALE = "m"
FEMALE = "f"
UNSPECIFIED = "-"
GENDERS = {(MALE, _("male")),
           (FEMALE, _("female")),
           (UNSPECIFIED, _("don't want to answer"))}
GENDER = {MALE: _("male"),
          FEMALE: _("female"),
          UNSPECIFIED: _("don't want to answer")}
