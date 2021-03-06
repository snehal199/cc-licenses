import re

from django.shortcuts import get_object_or_404, render

from i18n import DEFAULT_LANGUAGE_CODE
from i18n.utils import active_translation, get_language_for_jurisdiction
from licenses.models import LegalCode, License

DEED_TEMPLATE_MAPPING = {  # CURRENTLY UNUSED
    # license_code : template name
    "sampling": "licenses/sampling_deed.html",
    "sampling+": "licenses/sampling_deed.html",
    "nc-sampling+": "licenses/sampling_deed.html",
    "devnations": "licenses/devnations_deed.html",
    "CC0": "licenses/zero_deed.html",
    "mark": "licenses/pdmark_deed.html",
    "publicdomain": "licenses/publicdomain_deed.html",
    # others use "licenses/standard_deed.html"
}


# For removing the deed.foo section of a deed url
REMOVE_DEED_URL_RE = re.compile(r"^(.*?/)(?:deed)?(?:\..*)?$")


def home(request):
    # Get the list of license codes and languages that occur among the 4.0 licenses
    # to let the template iterate over them as it likes.
    codes_for_40 = (
        License.objects.filter(version="4.0")
        .order_by("license_code")
        .distinct("license_code")
        .values_list("license_code", flat=True)
    )
    languages_for_40 = (
        LegalCode.objects.filter(license__version="4.0")
        .order_by("language_code")
        .distinct("language_code")
        .values_list("language_code", flat=True)
    )

    licenses_by_version = [
        ("4.0", codes_for_40, languages_for_40),
    ]

    context = {
        "licenses_by_version": licenses_by_version,
        # "licenses_by_code": licenses_by_code,
        "legalcodes": LegalCode.objects.filter(
            license__version="4.0", language_code__in=["en", "es", "ar", "de"]
        ).order_by("license__license_code", "language_code"),
    }
    return render(request, "home.html", context)


def view_license(request, license_code, version, jurisdiction=None, language_code=None):
    if language_code is None and jurisdiction:
        language_code = get_language_for_jurisdiction(jurisdiction)
    language_code = language_code or DEFAULT_LANGUAGE_CODE

    legalcode = get_object_or_404(
        LegalCode,
        license__license_code=license_code,
        license__version=version,
        license__jurisdiction_code=jurisdiction or "",
        language_code=language_code,
    )
    translation = legalcode.get_translation_object()
    with active_translation(translation):
        return render(
            request,
            "legalcode_40_page.html",
            {"legalcode": legalcode, "license": legalcode.license,},
        )


def view_deed(request, license_code, version, jurisdiction=None, language_code=None):
    if language_code is None and jurisdiction:
        language_code = get_language_for_jurisdiction(jurisdiction)
    language_code = language_code or DEFAULT_LANGUAGE_CODE

    legalcode = get_object_or_404(
        LegalCode,
        license__license_code=license_code,
        license__version=version,
        license__jurisdiction_code=jurisdiction or "",
        language_code=language_code,
    )
    translation = legalcode.get_translation_object()
    with active_translation(translation):
        return render(
            request,
            "deed_40.html",
            {"legalcode": legalcode, "license": legalcode.license,},
        )
