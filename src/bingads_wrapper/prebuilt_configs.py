from itertools import chain
from typing import Iterable, Literal, TypeVar
from dataclasses import dataclass

from keboola.component.exceptions import UserException

T = TypeVar('T')

Aggregation = Literal["Daily", "Hourly"]


def unique(*iterables: Iterable[T], check_already_unique: bool = True) -> list[T]:
    """Returns unique elements of provided iterbles in the order they first appear."""
    r = list(dict.fromkeys(chain.from_iterable(iterables)))
    if check_already_unique and len(tuple(chain.from_iterable(iterables))) != len(r):
        raise ValueError("Provided iterables had duplicate elements or their elements (partially) overlapped.")
    return r


@dataclass(slots=True, frozen=True)
class ColumnsAndPrimaryKey:
    columns: list[str]
    primary_key: list[str]

    def __post_init__(self):
        pk_not_in_columns = set(self.primary_key) - set(self.columns)
        if pk_not_in_columns:
            missing_col_string = ', '.join(pk_not_in_columns)
            raise ValueError(f'All primary key columns must be in columns.'
                             f' Primary key columns missing in columns: {missing_col_string}.')


@dataclass(slots=True, frozen=True)
class PrebuiltReportConfig:
    report_type: str
    columns_and_primary_key_by_aggregation: dict[Aggregation, ColumnsAndPrimaryKey]


COMMON_PRIMARY_KEY = (
    "AccountId",
    "TimePeriod",
    "CurrencyCode",
    "AdDistribution",
    "DeviceType",
    "Network",
)

RESTRICTED_PRIMARY_KEY = (
    "BidMatchType",
    "DeviceOS",
    "Goal",
    "GoalType",
    "TopVsOther",
)

AD_PRIMARY_KEY = ("AdId",)

AD_GROUP_PRIMARY_KEY = ("AdGroupId",)

CAMPAIGN_PRIMARY_KEY = ("CampaignId",)

LANGUAGE_PRIMARY_KEY = ("Language",)

CAMPAIGN_COLUMNS = (
    "CampaignStatus",
    "CustomParameters",
)

BUDGET_COLUMNS = (
    "BudgetName",
    "BudgetStatus",
    "BudgetAssociationStatus",
)

AVERAGE_METRICS = (
    "AverageCpc",
    "AverageCpm",
    "AveragePosition",
)

CONVERSION_METRICS = (
    "Conversions",
    "ConversionRate",
    "ConversionsQualified",
)

LOW_QUALITY_METRICS = (
    "LowQualityClicks",
    "LowQualityClicksPercent",
    "LowQualityConversionRate",
    "LowQualityConversions",
    "LowQualityConversionsQualified",
    "LowQualityGeneralClicks",
    "LowQualityImpressions",
    "LowQualityImpressionsPercent",
    "LowQualitySophisticatedClicks",
)

REVENUE_METRICS = (
    "Revenue",
    "RevenuePerAssist",
    "RevenuePerConversion",
)

ALL_REVENUE_METRICS = (
    "AllRevenue",
    "AllRevenuePerConversion",
)

IMPRESSION_METRICS = (
    "ImpressionLostToBudgetPercent",
    "ImpressionLostToRankAggPercent",
    "Impressions",
    "ImpressionSharePercent",
)

HISTORICAL_METRICS = (
    "HistoricalAdRelevance",
    "HistoricalExpectedCtr",
    "HistoricalLandingPageExperience",
    "HistoricalQualityScore",
)

COMMON_PERFORMANCE_METRICS = (
    "PhoneImpressions",
    "PhoneCalls",
    "Clicks",
    "Ctr",
    "Spend",
    "Impressions",
    "CostPerConversion",
    "Ptr",
    "Assists",
    "ReturnOnAdSpend",
    "CostPerAssist",
    "AllConversionsQualified",
    "ViewThroughConversionsQualified",
)

COMMON_RESTRICTING_PERFORMANCE_METRICS = (
    "AbsoluteTopImpressionRatePercent",
    "AbsoluteTopImpressionShareLostToBudgetPercent",
    "AbsoluteTopImpressionShareLostToRankPercent",
    "AbsoluteTopImpressionSharePercent",
    # "AudienceImpressionLostToBudgetPercent",
    # "AudienceImpressionLostToRankPercent",
    # "AudienceImpressionSharePercent",
    "ClickSharePercent",
    "ExactMatchImpressionSharePercent",
    "ImpressionLostToBudgetPercent",
    "ImpressionLostToRankAggPercent",
    # "ImpressionSharePercent",
    # "RelativeCtr",
)

CAMPAIGN_METRICS = (
    "QualityScore",
    "ExpectedCtr",
    "AdRelevance",
    "LandingPageExperience",
)

ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY = unique(
    COMMON_PRIMARY_KEY,
    ("DeliveredMatchType",),
)

ACCOUNT_PERFORMANCE_COLUMNS_AND_PK = ColumnsAndPrimaryKey(
    columns=unique(
        ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
        RESTRICTED_PRIMARY_KEY,
        COMMON_PERFORMANCE_METRICS,
        AVERAGE_METRICS,
        CONVERSION_METRICS,
        LOW_QUALITY_METRICS,
        REVENUE_METRICS,
    ),
    primary_key=unique(
        ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
        RESTRICTED_PRIMARY_KEY,
    ),
)

CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY = unique(
    ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
    CAMPAIGN_PRIMARY_KEY,
)

CAMPAIGN_PERFORMANCE_COMMON_COLUMNS = unique(
    CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
    CAMPAIGN_COLUMNS,
    CAMPAIGN_METRICS,
    COMMON_PERFORMANCE_METRICS,
    ALL_REVENUE_METRICS,
    AVERAGE_METRICS,
    CONVERSION_METRICS,
    LOW_QUALITY_METRICS,
    REVENUE_METRICS,
)

AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY = unique(
    CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
    AD_GROUP_PRIMARY_KEY,
    LANGUAGE_PRIMARY_KEY,
)

AD_GROUP_PERFORMANCE_COMMON_COLUMNS = unique(
    AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
    COMMON_PERFORMANCE_METRICS,
    CAMPAIGN_METRICS,
    CAMPAIGN_COLUMNS,
    ("FinalUrlSuffix",),
    ALL_REVENUE_METRICS,
    AVERAGE_METRICS,
    CONVERSION_METRICS,
    REVENUE_METRICS,
)

AD_GROUP_PERFORMANCE_RESTRICTED_PRIMARY_KEY = unique(
    AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
    RESTRICTED_PRIMARY_KEY,
)

# PRODUCT_DIMENSION_PERFORMANCE_COLUMNS_AND_PK = # TODO: remove unless needed

PREBUILT_CONFIGS = {
    "AccountPerformance":
        PrebuiltReportConfig(
            report_type="AccountPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily": ACCOUNT_PERFORMANCE_COLUMNS_AND_PK,
                "Hourly": ACCOUNT_PERFORMANCE_COLUMNS_AND_PK,
            },
        ),
    "AccountImpressionPerformance":
        PrebuiltReportConfig(
            report_type="AccountPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
                            COMMON_PERFORMANCE_METRICS,
                            COMMON_RESTRICTING_PERFORMANCE_METRICS,
                            AVERAGE_METRICS,
                            CONVERSION_METRICS,
                            LOW_QUALITY_METRICS,
                            REVENUE_METRICS,
                            IMPRESSION_METRICS,
                            check_already_unique=False,
                        ),
                        primary_key=ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
                            COMMON_PERFORMANCE_METRICS,
                            AVERAGE_METRICS,
                            CONVERSION_METRICS,
                            LOW_QUALITY_METRICS,
                            REVENUE_METRICS,
                        ),
                        primary_key=ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
                    ),
            },
        ),
    "AdGroupPerformance":
        PrebuiltReportConfig(
            report_type="AdGroupPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            AD_GROUP_PERFORMANCE_COMMON_COLUMNS,
                            RESTRICTED_PRIMARY_KEY,
                            HISTORICAL_METRICS,
                        ),
                        primary_key=unique(
                            AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
                            RESTRICTED_PRIMARY_KEY,
                        ),
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            AD_GROUP_PERFORMANCE_COMMON_COLUMNS,
                            RESTRICTED_PRIMARY_KEY,
                        ),
                        primary_key=unique(
                            AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
                            RESTRICTED_PRIMARY_KEY,
                        ),
                    )
            },
        ),
    "AdGroupImpressionPerformance":
        PrebuiltReportConfig(
            report_type="AdGroupPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            AD_GROUP_PERFORMANCE_COMMON_COLUMNS,
                            COMMON_RESTRICTING_PERFORMANCE_METRICS,
                            IMPRESSION_METRICS,
                            HISTORICAL_METRICS,
                            check_already_unique=False,
                        ),
                        primary_key=AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            AD_GROUP_PERFORMANCE_COMMON_COLUMNS,
                            COMMON_RESTRICTING_PERFORMANCE_METRICS,
                        ),
                        primary_key=AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
                    )
            },
        ),
    "CampaignPerformance":
        PrebuiltReportConfig(
            report_type="CampaignPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            CAMPAIGN_PERFORMANCE_COMMON_COLUMNS,
                            RESTRICTED_PRIMARY_KEY,
                            BUDGET_COLUMNS,
                            HISTORICAL_METRICS,
                        ),
                        primary_key=unique(
                            CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
                            RESTRICTED_PRIMARY_KEY,
                        ),
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            CAMPAIGN_PERFORMANCE_COMMON_COLUMNS,
                            RESTRICTED_PRIMARY_KEY,
                            BUDGET_COLUMNS,
                        ),
                        primary_key=unique(
                            CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
                            RESTRICTED_PRIMARY_KEY,
                        ),
                    ),
            },
        ),
    "CampaignImpressionPerformance":
        PrebuiltReportConfig(
            report_type="CampaignPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            CAMPAIGN_PERFORMANCE_COMMON_COLUMNS,
                            COMMON_RESTRICTING_PERFORMANCE_METRICS,
                            IMPRESSION_METRICS,
                            HISTORICAL_METRICS,
                            check_already_unique=False,
                        ),
                        primary_key=CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            CAMPAIGN_PERFORMANCE_COMMON_COLUMNS,
                            COMMON_RESTRICTING_PERFORMANCE_METRICS,
                        ),
                        primary_key=CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
                    ),
            },
        ),
}


def get_prebuilt_report_config(preset_name: str, aggregation: Aggregation) -> dict[str, str | list[str]]:
    try:
        config = PREBUILT_CONFIGS[preset_name]
        columns_and_primary_key = config.columns_and_primary_key_by_aggregation[aggregation]
        return {
            "report_type": config.report_type,
            "columns": columns_and_primary_key.columns,
            "primary_key": columns_and_primary_key.primary_key
        }
    except KeyError:
        raise UserException(f'Prebuilt report configuration for preset name "{preset_name}"'
                            f' and aggregation "{aggregation}" is not available.')


def __find_columns_containing_string_in_preset(preset_name: str,
                                               aggregation: Aggregation,
                                               s: str,
                                               in_primary_key: bool = False,
                                               case_sensitive: bool = False) -> list[str]:
    preset = get_prebuilt_report_config(preset_name, aggregation)
    columns = preset["columns"] if not in_primary_key else preset["primary_key"]
    if case_sensitive:

        def predicate(col: str):
            return s in col
    else:

        def predicate(col: str):
            return s.lower() in col.lower()

    return [col for col in columns if predicate(col)]


if __name__ == "__main__":
    import json
    from pathlib import Path
    with open("data/prebuilt_config_preset_names.json", 'w') as out_f:
        json.dump(list(PREBUILT_CONFIGS.keys()), out_f)

    reference_presets_path = Path(__file__).parent / "reference_presets.json"
    reference_presets = json.loads(reference_presets_path.read_text())

    def compare_prebuilt_config_to_reference(config_name: str, config: PrebuiltReportConfig):
        reference_preset = reference_presets[config_name]
        report = dict()
        for aggregation in config.columns_and_primary_key_by_aggregation.keys():
            reference_columns_and_primary_key = ColumnsAndPrimaryKey(
                columns=reference_preset[aggregation]["columns"],
                primary_key=reference_preset[aggregation]["primary_key"])
            reference_columns = reference_columns_and_primary_key.columns
            config_columns_and_primary_key = config.columns_and_primary_key_by_aggregation[aggregation]
            config_columns = config_columns_and_primary_key.columns
            missing_columns = [col for col in reference_columns if col not in config_columns]
            extra_columns = [col for col in config_columns if col not in reference_columns]
            report[aggregation] = {"missing_columns": missing_columns, "extra_columns": extra_columns}
        return config_name, report

    reference_comparison_report = {
        config_name: report for config_name, report in (compare_prebuilt_config_to_reference(config_name, config)
                                                        for config_name, config in PREBUILT_CONFIGS.items())
    }
    with open("data/reference_comparison_report.json", 'w') as out_f:
        json.dump(reference_comparison_report, out_f)
