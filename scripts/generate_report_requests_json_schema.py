import json
import pkgutil
import xml.etree.ElementTree as ET

# from pathlib import Path

# from suds.sudsobject import Object

# from bingads.service_client import ServiceClient

# script_path = Path(__file__)
# script_dir = script_path.parent
# with open(script_dir / "all_report_types.json", "r") as f:
#     report_types = json.load(f)

# service_client = ServiceClient("ReportingService", 13, environment="production")
# factory = service_client.factory

xml_bytes = pkgutil.get_data("bingads.v13", "proxies/production/reporting_service.xml")

xml_root_element = ET.fromstring(xml_bytes)
report_request_base_type_def = xml_root_element.find(
    ".//{http://www.w3.org/2001/XMLSchema}complexType[@name='ReportRequest']"
)
report_request_subtype_defs = xml_root_element.findall(
    ".//{http://www.w3.org/2001/XMLSchema}extension[@base='tns:ReportRequest']../.."
)

schema_template_dict = {
    "type": "object",
    "title": "Reporting download request",
    "description": "Specification to request data via the Reporting API",
    "required": [
        "type",
        "format_version",
        "return_only_complete_data",
        "columns",
        "report_type",
        "time",
    ],
    "properties": {
        "type": {
            "title": "Type",
            "description": "Type of the download request",
            "type": "string",
            "enum": ["Reporting"],
            "propertyOrder": 1000,
        },
        "format_version": {
            "title": "Format version",
            "description": "Determines the format for certain fields in the downloaded report file.",
            "type": "string",
            "enum": ["1.0", "2.0"],
            "default": "2.0",
            "propertyOrder": 2000,
        },
        "return_only_complete_data": {
            "title": "Return only complete data",
            "description": "Determines whether or not the service must ensure that all the data has been processed and is available.",
            "type": "boolean",
            "format": "checkbox",
            "default": True,
            "propertyOrder": 3000,
        },
        "report_type": {
            "title": "Report type",
            "description": "The reporting service provides reports that you can use to track finances, measure ad performance, and adjust settings to optimize your budget or campaign. The service supports the majority of popular reports available in the Microsoft Advertising web application.",
            "type": "string",
            "enum": [],
            "default": "2.0",
            "propertyOrder": 2000,
        },
        "time": {
            "type": "object",
            "title": "Reporting download request",
            "description": "Specification to request data via the Reporting API",
            "required": [
                "type",
                "format_version",
                "return_only_complete_data",
                "time",
                "report_type",
            ],
            "properties": {},
        },
    },
    "additionalProperties": False,
}


def generate_report_request_json_schema_dict(
    report_request_subtype_def: ET.Element,
) -> dict:
    type_name = report_request_subtype_def.attrib["name"]
    column_names = report_request_subtype_def

    pass


for report_type in report_request_subtype_defs:
    generate_report_request_json_schema_dict(report_type)
