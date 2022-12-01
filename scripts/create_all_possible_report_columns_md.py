import pkgutil
import xml.etree.ElementTree as ET

xml_root_element = ET.fromstring(pkgutil.get_data("bingads.v13", "proxies/production/reporting_service.xml"))


def generate_report_request_md_fragment(report_request_subtype_element: ET.Element) -> str:
    subtype_name: str = report_request_subtype_element.attrib["name"].replace("ReportRequest", "")

    columns_type_element = xml_root_element.find(".//{http://www.w3.org/2001/XMLSchema}simpleType[@name='" +
                                                 subtype_name + "ReportColumn']")
    columns_enum_elements = columns_type_element.findall(".//{http://www.w3.org/2001/XMLSchema}enumeration")
    column_names = [columns_enum_element.attrib["value"] for columns_enum_element in columns_enum_elements]
    assert len(column_names) > 0
    column_str = ", ".join(column_names)

    return f"## {subtype_name} Report\n`{column_str}`"


if __name__ == '__main__':
    report_request_subtype_defs = xml_root_element.findall(
        ".//{http://www.w3.org/2001/XMLSchema}extension[@base='tns:ReportRequest']../..")

    output_md = ("# Possible columns for each report type\n" + "\n".join(
        generate_report_request_md_fragment(report_subtype_element)
        for report_subtype_element in report_request_subtype_defs))

    with open("docs/reports_available_columns.md", 'w') as out_f:
        out_f.write(output_md)
