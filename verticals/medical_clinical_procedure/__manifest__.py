
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Clinical Procedure",
    "summary": "Medical Procedures and Procedure requests",
    "version": "1.0.1.0.0",
    "author": "Tele Community",
    "category": "Medical",
    "website": "https://health.tele.studio",
    "license": "LGPL-3",
    "depends": [
        "medical_workflow",
        "medical_clinical",
        "medical_administration_location",
    ],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/medical_workflow.xml",
        "wizard/medical_procedure_request_make_procedure_view.xml",
        "views/medical_request_views.xml",
        "views/medical_procedure_view.xml",
        "views/medical_procedure_request_view.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
