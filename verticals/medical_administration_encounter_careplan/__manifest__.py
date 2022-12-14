
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Encounter careplan",
    "summary": "Joins careplans and encounters",
    "version": "1.0.1.0.0",
    "author": "Tele Community",
    "website": "https://health.tele.studio",
    "category": "Medical",
    "license": "LGPL-3",
    "depends": [
        "medical_administration_encounter",
        "medical_clinical_careplan",
    ],
    "data": [
        "security/medical_security.xml",
        "views/medical_encounter_view.xml",
        "views/medical_request_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
