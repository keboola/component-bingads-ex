import pkgutil
import xml.etree.ElementTree as ET

xml_root_element = ET.fromstring(pkgutil.get_data("bingads.v13", "proxies/production/reporting_service.xml"))


def _generate_report_request_md_fragment(report_request_subtype_element: ET.Element) -> dict:
    subtype_name: str = report_request_subtype_element.attrib["name"].replace("ReportRequest", "")

    columns_type_element = xml_root_element.find(".//{http://www.w3.org/2001/XMLSchema}simpleType[@name='" +
                                                 subtype_name + "ReportColumn']")
    columns_enum_elements = columns_type_element.findall(".//{http://www.w3.org/2001/XMLSchema}enumeration")
    column_names = [columns_enum_element.attrib["value"] for columns_enum_element in columns_enum_elements]
    assert len(column_names) > 0

    return {subtype_name: column_names}


def get_report_available_columns() -> dict:
    report_request_subtype_defs = xml_root_element.findall(
        ".//{http://www.w3.org/2001/XMLSchema}extension[@base='tns:ReportRequest']../..")

    result_dict = {}
    for report_subtype_element in report_request_subtype_defs:
        result_dict = {**result_dict, **_generate_report_request_md_fragment(report_subtype_element)}

    return result_dict
