"""
Helpers for the Microsoft Advertising REST API (SDK ``msads``, import namespace ``bingads``).

Background
----------
Microsoft retires the SOAP interface of the Microsoft Advertising API on 2027-01-31.
The SDK moved from SOAP (``suds``) to REST. The REST build keeps the ``bingads`` import
namespace and the ``ServiceClient`` class, but the object model below it changed:

* Request and response objects are Pydantic models from ``openapi_client.models``,
  not dynamically generated ``suds`` objects.
* ``ServiceClient.factory.create("<Type>ReportRequest")`` does not resolve report types.
  Report request models must be imported from ``openapi_client.models``.
* Nested fields (``Time``, ``Scope``, ``Columns``) default to ``None``. ``suds`` created
  them on first access. Pydantic does not, so each nested model must be built explicitly.
* Enum fields are plain values. The ``suds`` ``.set(value)`` method does not exist.
* Field validation runs on assignment, so a value of the wrong type raises immediately.

This module holds the small amount of glue that the rest of the package needs.
"""

import openapi_client.models as rest_models
from openapi_client.model_utils import enable_alias_support

# Lets code read and write model fields with their PascalCase API names
# (``request.ExcludeReportHeader``) instead of the generated snake_case names.
# This must run before any model instance is created, so it is called at import time
# and the package ``__init__`` imports this module first.
enable_alias_support()


class UnsupportedReportTypeError(Exception):
    """Raised when the SDK has no request model for a configured report type."""


def create_report_request(report_type: str):
    """
    Build an empty request model for ``report_type``.

    Replaces ``ServiceClient.factory.create(report_type + "ReportRequest")``, which the
    REST SDK no longer supports for reporting types.
    """
    model_name = f"{report_type}ReportRequest"
    model = getattr(rest_models, model_name, None)
    if model is None:
        raise UnsupportedReportTypeError(
            f"The Microsoft Advertising REST API has no report request type '{model_name}'."
        )
    return model()


def declares_field(model_instance, field_alias: str) -> bool:
    """
    Report whether the model declares the field ``field_alias`` (a PascalCase API name).

    Under ``suds`` the code used ``hasattr`` to find out whether a report type supports
    an element such as ``Time`` or ``Scope``. Pydantic declares every optional field on
    the class, so ``hasattr`` is now always true and cannot answer that question.
    This checks the model's declared fields instead, which keeps the original meaning.
    """
    for field in type(model_instance).model_fields.values():
        if field.alias == field_alias:
            return True
    return False


def build_nested(model_instance, field_alias: str, **values):
    """
    Build the nested model that ``field_alias`` declares, and set it on ``model_instance``.

    The concrete type depends on the report type. ``Scope``, for example, is
    ``AccountReportScope`` on some reports and ``AccountThroughAdGroupReportScope`` on
    others. The type is read from the field annotation so the correct model is used.
    """
    model_fields = type(model_instance).model_fields
    field = next((f for f in model_fields.values() if f.alias == field_alias), None)
    if field is None:
        raise AttributeError(f"{type(model_instance).__name__} has no field '{field_alias}'.")

    nested_type = _unwrap_optional(field.annotation)
    nested = nested_type(**values)
    setattr(model_instance, field_alias, nested)
    return nested


def _unwrap_optional(annotation):
    """Return ``T`` for an annotation of ``Optional[T]``, otherwise the annotation itself."""
    args = getattr(annotation, "__args__", None)
    if not args:
        return annotation
    non_none = [arg for arg in args if arg is not type(None)]  # noqa: E721
    return non_none[0] if non_none else annotation


def _enum_type(annotation):
    """Return the Enum class an annotation holds, directly or inside a list. Else None."""
    import enum
    import typing

    candidates = [annotation]
    while candidates:
        current = candidates.pop()
        if isinstance(current, type) and issubclass(current, enum.Enum):
            return current
        args = typing.get_args(current)
        candidates.extend(arg for arg in args if arg is not type(None))  # noqa: E721
    return None


def set_field(model_instance, field_alias: str, value):
    """
    Set a field, converting plain strings to the enum members the model declares.

    The PascalCase alias patch writes attributes without running Pydantic validation,
    so a plain string stays a string on an enum field. That serializes with a warning
    and leaves the model inconsistent. Converting here keeps the model well typed.
    An unknown value is left as it is, so the API reports the invalid value rather than
    this code failing with a less helpful error.
    """
    model_fields = type(model_instance).model_fields
    field = next((f for f in model_fields.values() if f.alias == field_alias), None)
    enum_class = _enum_type(field.annotation) if field is not None else None

    if enum_class is not None and value is not None:
        if isinstance(value, list):
            value = [_to_enum(enum_class, item) for item in value]
        else:
            value = _to_enum(enum_class, value)

    setattr(model_instance, field_alias, value)
    return value


def _to_enum(enum_class, value):
    """Convert one value to a member of ``enum_class``, or return it unchanged."""
    if isinstance(value, enum_class):
        return value
    try:
        return enum_class(value)
    except ValueError:
        return value
