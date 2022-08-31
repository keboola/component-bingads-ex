import json
import pkgutil
from typing import Any, Callable, List
import xml.etree.ElementTree as ET
from pathlib import Path
from copy import deepcopy


script_path = Path(__file__)
script_dir = script_path.parent
fragments_dir = script_dir / "report_request_json_schema_fragments"
with open(fragments_dir / "time_property.json", "r") as f:
    time_property: dict = json.load(f)
with open(fragments_dir / "aggregation_property.json", "r") as f:
    aggregation_property: dict = json.load(f)
with open(fragments_dir / "columns_property_template.json", "r") as f:
    columns_property_template: dict = json.load(f)
with open(fragments_dir / "primary_key_property_template.json", "r") as f:
    primary_key_property_template: dict = json.load(f)
with open(fragments_dir / "report_request_template.json", "r") as f:
    report_request_template: dict = json.load(f)

xml_bytes = pkgutil.get_data("bingads.v13", "proxies/production/reporting_service.xml")

xml_root_element = ET.fromstring(xml_bytes)
# report_request_base_type_def = xml_root_element.find(
#     ".//{http://www.w3.org/2001/XMLSchema}complexType[@name='ReportRequest']"
# )
report_request_subtype_defs = xml_root_element.findall(
    ".//{http://www.w3.org/2001/XMLSchema}extension[@base='tns:ReportRequest']../.."
)


def apply_recursive(func: Callable[[Any], Any], obj: dict | list | Any):
    if isinstance(obj, dict):  # if dict, apply to each key
        return {k: apply_recursive(func, v) for k, v in obj.items()}
    elif isinstance(obj, list):  # if list, apply to each element
        return [apply_recursive(func, elem) for elem in obj]
    else:
        return func(obj)


REPORT_SUBTYPE_PLACEHOLDER = "{REPORT_SUBTYPE}"


def generate_report_request_json_schema_dict(
    report_request_subtype_element: ET.Element,
) -> dict:
    subtype_name: str = report_request_subtype_element.attrib["name"].replace(
        "ReportRequest", ""
    )

    def placeholder_replacer(v: str | Any) -> str | Any:
        if isinstance(v, str):
            return v.replace(REPORT_SUBTYPE_PLACEHOLDER, subtype_name)
        else:
            return v

    output_schema_dict = apply_recursive(placeholder_replacer, report_request_template)
    required_properties: List[str] = output_schema_dict["required"]

    aggregation_is_present = bool(
        report_request_subtype_element.find(
            ".//{http://www.w3.org/2001/XMLSchema}element[@name='Aggregation']"
        )
        is not None
    )
    if aggregation_is_present:
        output_schema_dict["properties"] = (
            output_schema_dict["properties"] | aggregation_property
        )
        required_properties.append(next(iter(aggregation_property)))

    time_is_present = bool(
        report_request_subtype_element.find(
            ".//{http://www.w3.org/2001/XMLSchema}element[@name='Time']"
        )
        is not None
    )
    if time_is_present:
        output_schema_dict["properties"] = (
            output_schema_dict["properties"] | time_property
        )
        required_properties.append(next(iter(time_property)))

    columns_type_element = xml_root_element.find(
        ".//{http://www.w3.org/2001/XMLSchema}simpleType[@name='"
        + subtype_name
        + "ReportColumn']"
    )
    columns_enum_elements = columns_type_element.findall(
        ".//{http://www.w3.org/2001/XMLSchema}enumeration"
    )
    column_names = [
        columns_enum_element.attrib["value"]
        for columns_enum_element in columns_enum_elements
    ]
    assert len(column_names) > 0

    columns_property = deepcopy(columns_property_template)
    columns_property["columns"]["items"]["enum"] = column_names
    output_schema_dict["properties"] = (
        output_schema_dict["properties"] | columns_property
    )
    required_properties.append(next(iter(columns_property)))

    primary_key_property = deepcopy(primary_key_property_template)
    primary_key_property["primary_key"]["items"]["enum"] = column_names
    output_schema_dict["properties"] = (
        output_schema_dict["properties"] | primary_key_property
    )
    required_properties.append(next(iter(primary_key_property)))

    return output_schema_dict


output_schema_fragments = [
    generate_report_request_json_schema_dict(report_subtype_element)
    for report_subtype_element in report_request_subtype_defs
]

if __name__ == "__main__":
    # with open(script_dir / "report_subtype_schema_fragments.json", "w") as f:
    #     json.dump(output_schema_fragments, f)
    component_config_dir = script_dir.parent / "component_config"
    config_row_schema = component_config_dir / "configRowSchema.json"
    with open(config_row_schema, "r") as f:
        config_row_schema_dict: dict = json.load(f)
    config_row_schema_dict["definitions"]["report_download_request"][
        "oneOf"
    ] = output_schema_fragments
    with open(config_row_schema, "w") as f:
        json.dump(config_row_schema_dict, f)
