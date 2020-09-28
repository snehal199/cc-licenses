from unittest import mock
from unittest.mock import MagicMock, call

import polib
from django.test import TestCase, override_settings
from django.utils import translation
from django.utils.translation import override

from i18n import DEFAULT_LANGUAGE_CODE
from i18n.translation import Translation
from licenses import FREEDOM_LEVEL_MAX, FREEDOM_LEVEL_MID, FREEDOM_LEVEL_MIN
from licenses.models import LegalCode
from licenses.tests.factories import LegalCodeFactory, LicenseFactory
from licenses.tests.test_transifex import TEST_TRANSIFEX_SETTINGS
from licenses.transifex import TransifexHelper


class LegalCodeModelTest(TestCase):
    fixtures = ["licenses.json"]

    def test_str(self):
        legal_code = LegalCode.objects.first()
        self.assertEqual(
            str(legal_code),
            f"LegalCode<{legal_code.language_code}, {legal_code.license.about}>",
        )

    @override_settings(TRANSLATION_REPOSITORY_DIRECTORY="/foo")
    def test_translation_filename(self):
        data = [
            # ("expected", license_code, version, jurisdiction, language),
            ("/foo/translations/by-sa/0.3/by-sa_0.3_de.po", "by-sa", "0.3", "", "de"),
            (
                "/foo/translations/by-sa/0.3/by-sa_0.3_xx_de.po",
                "by-sa",
                "0.3",
                "xx",
                "de",
            ),
        ]

        for expected, license_code, version, jurisdiction, language in data:
            with self.subTest(expected):
                license = LicenseFactory(
                    license_code=license_code,
                    version=version,
                    jurisdiction_code=jurisdiction,
                )
                self.assertEqual(
                    expected,
                    LegalCodeFactory(
                        license=license, language_code=language
                    ).translation_filename(),
                )

    def test_license_url(self):
        lc = LegalCodeFactory()
        with mock.patch("licenses.models.build_license_url") as mock_build:
            lc.license_url()
        self.assertEqual(
            [
                call(
                    lc.license.license_code,
                    lc.license.version,
                    lc.license.jurisdiction_code,
                    lc.language_code,
                )
            ],
            mock_build.call_args_list,
        )

    def test_deed_url(self):
        lc = LegalCodeFactory()
        with mock.patch("licenses.models.build_deed_url") as mock_build:
            lc.deed_url()
        self.assertEqual(
            [
                call(
                    lc.license.license_code,
                    lc.license.version,
                    lc.license.jurisdiction_code,
                    lc.language_code,
                )
            ],
            mock_build.call_args_list,
        )

    def help_test_downstreams(self, code):
        # mock the translation
        with mock.patch.object(
            LegalCode, "get_translation_object"
        ) as mock_get_translation_object:
            mock_get_translation_object.return_value.translate.return_value = "qwerty"
            return LegalCodeFactory(license__license_code=code).downstreams()

    def test_downstreams(self):
        with self.subTest("by"):
            result = self.help_test_downstreams("by")
            expected = [
                {
                    "id": "s2a5A_offer",
                    "msgid_name": "s2a5_license_grant_downstream_offer_name",
                    "msgid_text": "s2a5_license_grant_downstream_offer_text",
                    "name_translation": "qwerty",
                    "text_translation": "qwerty",
                },
                {
                    "id": "s2a5B_no_restrictions",
                    "msgid_name": "s2a5_license_grant_downstream_no_restrictions_name",
                    "msgid_text": "s2a5_license_grant_downstream_no_restrictions_text",
                    "name_translation": "qwerty",
                    "text_translation": "qwerty",
                },
            ]
            self.assertEqual(expected, result)
        with self.subTest("by-sa"):
            result = self.help_test_downstreams("by-sa")
            expected = [
                {
                    "id": "s2a5A_offer",
                    "msgid_name": "s2a5_license_grant_downstream_offer_name",
                    "msgid_text": "s2a5_license_grant_downstream_offer_text",
                    "name_translation": "qwerty",
                    "text_translation": "qwerty",
                },
                {
                    "id": "s2a5B_adapted_material",
                    "msgid_name": "s2a5_license_grant_downstream_adapted_material_name",
                    "msgid_text": "s2a5_license_grant_downstream_adapted_material_text",
                    "name_translation": "qwerty",
                    "text_translation": "qwerty",
                },
                {
                    "id": "s2a5C_no_restrictions",
                    "msgid_name": "s2a5_license_grant_downstream_no_restrictions_name",
                    "msgid_text": "s2a5_license_grant_downstream_no_restrictions_text",
                    "name_translation": "qwerty",
                    "text_translation": "qwerty",
                },
            ]

            self.assertEqual(expected, result)
        with self.subTest("by-nc-sa"):
            result = self.help_test_downstreams("by-nc-sa")
            expected = [
                {
                    "id": "s2a5A_offer",
                    "msgid_name": "s2a5_license_grant_downstream_offer_name",
                    "msgid_text": "s2a5_license_grant_downstream_offer_text",
                    "name_translation": "qwerty",
                    "text_translation": "qwerty",
                },
                {
                    "id": "s2a5B_adapted_material",
                    "msgid_name": "s2a5_license_grant_downstream_adapted_material_name",
                    "msgid_text": "s2a5_license_grant_downstream_adapted_material_text",
                    "name_translation": "qwerty",
                    "text_translation": "qwerty",
                },
                {
                    "id": "s2a5C_no_restrictions",
                    "msgid_name": "s2a5_license_grant_downstream_no_restrictions_name",
                    "msgid_text": "s2a5_license_grant_downstream_no_restrictions_text",
                    "name_translation": "qwerty",
                    "text_translation": "qwerty",
                },
            ]
            self.assertEqual(expected, result)

    def test_definitions(self):
        codes = ["by", "by-nc", "by-nc-nd", "by-nc-sa", "by-nd", "by-sa"]
        for code in codes:
            with self.subTest(code=code):
                lc = LegalCodeFactory(license__license_code=code)
                # mock the translation
                with mock.patch.object(
                    LegalCode, "get_translation_object"
                ) as mock_get_translation_object:
                    mock_get_translation_object.return_value.translate.return_value = (
                        "qwerty"
                    )
                    result = lc.definitions()
                self.assertEqual(
                    {
                        "id": "s1a",
                        "msgid": "s1_definitions_adapted_material",
                        "translation": "qwerty",
                    },
                    result[0],
                )
                self.assertEqual("s1_definitions_you", result[-1]["msgid"])

    def test_convert_pofile_to_english_message_ids(self):
        english_pofile_content = """
msgid ""
msgstr ""
"Project-Id-Version: by-nd-4.0\n"
"Language: en\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"

msgid "license_medium"
msgstr "Attribution-NoDerivatives 4.0 International"

msgid "key2"
msgstr "English message 2"
        """
        english_pofile = polib.pofile(pofile=english_pofile_content)
        # There's 2 messages, the other one on input got turned into metadata
        self.assertEqual(2, len(english_pofile))
        spanish_pofile_content = """
msgid ""
msgstr ""
"Project-Id-Version: by-nd-4.0\n"
"Language: es\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"

msgid "license_medium"
msgstr "Atribución/Reconocimiento-SinDerivados 4.0 Internacional"

msgid "key2"
msgstr "Spanish message 2"
        """
        # Create spanish pofile object, with a non-default parameter to make
        # sure they get copied over.
        spanish_pofile = polib.pofile(pofile=spanish_pofile_content, wrapwidth=99)
        self.assertEqual(2, len(spanish_pofile))

        legalcode = LegalCodeFactory(language_code="es")
        with mock.patch.object(legalcode, "get_english_pofile") as mock_gep:
            mock_gep.return_value = english_pofile
            with mock.patch.object(legalcode, "get_pofile") as mock_gp:
                mock_gp.return_value = spanish_pofile

                new_pofile = legalcode.get_pofile_with_english_msgids()

        self.assertEqual(99, new_pofile.wrapwidth)
        self.assertEqual(2, len(new_pofile))  # 2 messages
        translations = {entry.msgid: entry.msgstr for entry in new_pofile}
        self.assertEqual(
            {
                "English message 2": "Spanish message 2",
                "Attribution-NoDerivatives 4.0 International": "Atribución/Reconocimiento-SinDerivados 4.0 Internacional",
            },
            translations,
        )

    def test_get_english_pofile_from_non_english_legalcode(self):
        license = LicenseFactory()
        LegalCodeFactory(license=license, language_code=DEFAULT_LANGUAGE_CODE)
        french_legalcode = LegalCodeFactory(license=license, language_code="fr")
        test_pofile = polib.POFile()
        with mock.patch.object(LegalCode, "get_pofile") as mock_egp:
            mock_egp.return_value = test_pofile
            result = french_legalcode.get_english_pofile()
        mock_egp.assert_called_with()
        self.assertEqual(test_pofile, result)

    def test_get_english_pofile_from_english_legalcode(self):
        license = LicenseFactory()
        english_legalcode = LegalCodeFactory(
            license=license, language_code=DEFAULT_LANGUAGE_CODE
        )
        test_pofile = polib.POFile()
        with mock.patch.object(english_legalcode, "get_pofile") as mock_egp:
            mock_egp.return_value = test_pofile
            result = english_legalcode.get_english_pofile()
        mock_egp.assert_called_with()
        self.assertEqual(test_pofile, result)

    def test_get_pofile(self):
        legalcode = LegalCodeFactory()
        test_pofile = polib.POFile()
        test_translation_object = MagicMock()
        test_translation_object.pofile = test_pofile
        with mock.patch.object(legalcode, "get_translation_object") as mock_gto:
            mock_gto.return_value = test_translation_object
            result = legalcode.get_pofile()
        mock_gto.assert_called_with()
        self.assertEqual(test_pofile, result)

    @override_settings(TRANSLATION_REPOSITORY_DIRECTORY="/some/dir")
    def test_get_translation_object(self):
        legalcode = LegalCodeFactory(
            license__version="4.0", license__license_code="by-sa", language_code="de"
        )
        import i18n.translation

        i18n.translation.get_translation_object.cache_clear()
        with mock.patch("i18n.translation.Translation") as mock_t:
            legalcode.get_translation_object()
        mock_t.assert_called_with(
            "/some/dir/translations/by-sa/4.0/by-sa_4.0_de.po", "de"
        )

    def test_branch_name(self):
        legalcode = LegalCodeFactory(
            license__version="4.0", license__license_code="by-sa", language_code="de"
        )
        self.assertEqual("cc4-de", legalcode.branch_name())

        legalcode = LegalCodeFactory(
            license__version="3.5", license__license_code="other", language_code="de"
        )
        self.assertEqual("other-35-de", legalcode.branch_name())

        legalcode = LegalCodeFactory(
            license__version="3.5",
            license__license_code="other",
            language_code="de",
            license__jurisdiction_code="xyz",
        )
        self.assertEqual("other-35-de-xyz", legalcode.branch_name())


# Many of these tests mostly are based on whether the metadata import worked right, and
# we're not importing metadata for the time being.
class LicenseModelTest(TestCase):
    # fixtures = ["licenses.json"]

    def test_get_legalcode_for_language_code(self):
        license = LicenseFactory()

        lc_pt = LegalCodeFactory(license=license, language_code="pt")
        lc_en = LegalCodeFactory(license=license, language_code="en")

        with override(language="pt"):
            result = license.get_legalcode_for_language_code(None)
            self.assertEqual(lc_pt.id, result.id)
        result = license.get_legalcode_for_language_code("pt")
        self.assertEqual(lc_pt.id, result.id)
        result = license.get_legalcode_for_language_code("en")
        self.assertEqual(lc_en.id, result.id)
        with self.assertRaises(LegalCode.DoesNotExist):
            license.get_legalcode_for_language_code("en_us")
        result = license.get_legalcode_for_language_code("en-us")
        self.assertEqual(lc_en.id, result.id)

    def test_resource_name(self):
        license = LicenseFactory(
            license_code="qwerty", version="2.7", jurisdiction_code="zys"
        )
        self.assertEqual("QWERTY 2.7 ZYS", license.resource_name)
        license = LicenseFactory(
            license_code="qwerty", version="2.7", jurisdiction_code=""
        )
        self.assertEqual("QWERTY 2.7", license.resource_name)

    def test_resource_slug(self):
        license = LicenseFactory(
            license_code="qwerty", version="2.7", jurisdiction_code="zys"
        )
        self.assertEqual("qwerty_27_zys", license.resource_slug)
        license = LicenseFactory(
            license_code="qwerty", version="2.7", jurisdiction_code=""
        )
        self.assertEqual("qwerty_27", license.resource_slug)

    def test_str(self):
        license = LicenseFactory(
            license_code="bx-oh", version="1.3", jurisdiction_code="any"
        )
        self.assertEqual(str(license), f"License<{license.about}>")

    def test_rdf(self):
        license = LicenseFactory(
            license_code="bx-oh", version="1.3", jurisdiction_code="any"
        )
        self.assertEqual("RDF Generation Not Implemented", license.rdf())

    # def test_default_language_code(self):
    #     license = LicenseFactory(license_code="bx-oh", version="1.3", jurisdiction_code="")
    #     self.assertEqual(DEFAULT_LANGUAGE_CODE, license.default_language_code())
    #     license = LicenseFactory(license_code="bx-oh", version="1.3", jurisdiction_code="fr")
    #     self.assertEqual("fr", license.default_language_code())

    # def test_get_deed_url(self):
    #     # https://creativecommons.org/licenses/by-sa/4.0/
    #     # https://creativecommons.org/licenses/by-sa/4.0/deed.es
    #     # https://creativecommons.org/licenses/by/3.0/es/
    #     # https://creativecommons.org/licenses/by/3.0/es/deed.fr
    #     license = LicenseFactory(license_code="bx-oh", version="1.3", jurisdiction_code="ae")
    #     self.assertEqual("/licenses/bx-oh/1.3/ae/", license.get_deed_url())
    #     license = LicenseFactory(license_code="bx-oh", version="1.3", jurisdiction_code="")
    #     self.assertEqual("/licenses/bx-oh/1.3/", license.get_deed_url())

    # def test_get_deed_url_for_language(self):
    #     license = LicenseFactory(license_code="bx-oh", version="1.3", jurisdiction_code="ae")
    #     self.assertEqual("/licenses/bx-oh/1.3/ae/deed.fr", license.get_deed_url_for_language("fr"))
    #     license = LicenseFactory(license_code="bx-oh", version="1.3", jurisdiction_code="")
    #     self.assertEqual("/licenses/bx-oh/1.3/deed.es", license.get_deed_url_for_language("es"))

    def test_sampling_plus(self):
        self.assertTrue(LicenseFactory(license_code="nc-sampling+").sampling_plus)
        self.assertTrue(LicenseFactory(license_code="sampling+").sampling_plus)
        self.assertFalse(LicenseFactory(license_code="sampling").sampling_plus)
        self.assertFalse(LicenseFactory(license_code="MIT").sampling_plus)
        self.assertFalse(LicenseFactory(license_code="by-nc-nd-sa").sampling_plus)

    def test_level_of_freedom(self):
        data = [
            ("by", FREEDOM_LEVEL_MAX),
            ("devnations", FREEDOM_LEVEL_MIN),
            ("sampling", FREEDOM_LEVEL_MIN),
            ("sampling+", FREEDOM_LEVEL_MID),
            ("by-nc", FREEDOM_LEVEL_MID),
            ("by-nd", FREEDOM_LEVEL_MID),
            ("by-sa", FREEDOM_LEVEL_MAX),
        ]
        for license_code, expected_freedom in data:
            with self.subTest(license_code):
                license = LicenseFactory(license_code=license_code)
                self.assertEqual(expected_freedom, license.level_of_freedom)

    def test_translated_title(self):
        license = LicenseFactory(
            license_code="by-nc-nd", jurisdiction_code="", version="4.0"
        )
        LegalCodeFactory(license=license, language_code="en")
        LegalCodeFactory(license=license, language_code="fr")

        # What a pain to get testing to work without .po files necessarily... FIXME make some test .po files
        with translation.override(language="fr"):
            lc_fr = license.get_legalcode_for_language_code(None)
        with translation.override(language="en"):
            lc_en = license.get_legalcode_for_language_code(None)

        mock_translation_object = MagicMock(autospec=Translation)
        expected = "Test License Title (fr)"
        mock_translation_object.translations = {"license_medium": expected}
        mock_get_translation_object_method = MagicMock(
            return_value=mock_translation_object
        )
        with mock.patch.object(
            lc_fr, "get_translation_object", mock_get_translation_object_method
        ):
            self.assertEqual(lc_fr.get_translation_object(), mock_translation_object)
            with mock.patch.object(
                license, "get_legalcode_for_language_code"
            ) as mock_get_lc:
                mock_get_lc.return_value = lc_fr

                with translation.override(language="fr"):
                    result = license.translated_title()
            self.assertEqual(
                expected, result,
            )

        expected = "Test License Title (en)"
        mock_translation_object.translations = {"license_medium": expected}
        with mock.patch.object(
            lc_en, "get_translation_object", mock_get_translation_object_method
        ):
            mock_get_legalcode_for_language_code = MagicMock(return_value=lc_en)
            with mock.patch.object(
                license,
                "get_legalcode_for_language_code",
                mock_get_legalcode_for_language_code,
            ):
                self.assertEqual(
                    lc_en.get_translation_object(), mock_translation_object
                )
                self.assertEqual(
                    expected, license.translated_title("en"),
                )
                self.assertEqual(
                    expected, license.translated_title(),
                )

    @override_settings(
        TRANSIFEX=TEST_TRANSIFEX_SETTINGS,
        TRANSLATION_REPOSITORY_DIRECTORY="/trans/repo",
    )
    def test_tx_upload_messages(self):
        legalcode = LegalCodeFactory(language_code=DEFAULT_LANGUAGE_CODE)
        license = legalcode.license
        with mock.patch.object(
            license, "get_legalcode_for_language_code"
        ) as mock_glflc:
            mock_glflc.return_value = legalcode
            with mock.patch.object(
                TransifexHelper, "upload_messages_to_transifex"
            ) as mock_umtt:
                license.tx_upload_messages()
        mock_glflc.assert_called_with("en")
        mock_umtt.assert_called_with(legalcode=legalcode)

    def test_superseded(self):
        lic1 = LicenseFactory()
        lic2 = LicenseFactory(is_replaced_by=lic1)
        self.assertTrue(lic2.superseded)
        self.assertFalse(lic1.superseded)
