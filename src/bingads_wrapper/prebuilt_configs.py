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
    "DeliveredMatchType",
)

RESTRICTED_PRIMARY_KEY = (
    "BidMatchType",
    "DeviceOS",
    "Goal",
    "GoalType",
    "TopVsOther",
)

AD_GROUP_PRIMARY_KEY = ("AdGroupId",)

CAMPAIGN_PRIMARY_KEY = ("CampaignId",)

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

RESTRICTING_PERFORMANCE_METRICS = (
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

ACCOUNT_PERFORMANCE_COLUMNS_AND_PK = ColumnsAndPrimaryKey(
    columns=unique(
        COMMON_PRIMARY_KEY,
        RESTRICTED_PRIMARY_KEY,
        COMMON_PERFORMANCE_METRICS,
        AVERAGE_METRICS,
        CONVERSION_METRICS,
        LOW_QUALITY_METRICS,
        REVENUE_METRICS,
    ),
    primary_key=unique(
        COMMON_PRIMARY_KEY,
        RESTRICTED_PRIMARY_KEY,
    ),
)

# ACCOUNT_IMPRESSION_PERFORMANCE_COLUMNS_AND_PK =

CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY = unique(
    COMMON_PRIMARY_KEY,
    CAMPAIGN_PRIMARY_KEY,
)

CAMPAIGN_PERFORMANCE_RESTRICTED_PRIMARY_KEY = unique(
    CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
    RESTRICTED_PRIMARY_KEY,
)

CAMPAIGN_PERFORMANCE_COMMON_COLUMNS = unique(
    CAMPAIGN_PERFORMANCE_RESTRICTED_PRIMARY_KEY,
    CAMPAIGN_COLUMNS,
    COMMON_PERFORMANCE_METRICS,
    ALL_REVENUE_METRICS,
    AVERAGE_METRICS,
    CONVERSION_METRICS,
    LOW_QUALITY_METRICS,
    REVENUE_METRICS,
    BUDGET_COLUMNS,
)

AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY = unique(
    CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
    AD_GROUP_PRIMARY_KEY,
    ("Language",),
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

AD_GROUP_PERFORMANCE_RESTRICTED_PRIMARY_KEY = unique(AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY, RESTRICTED_PRIMARY_KEY)

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
                            COMMON_PRIMARY_KEY,
                            COMMON_PERFORMANCE_METRICS,
                            RESTRICTING_PERFORMANCE_METRICS,
                            AVERAGE_METRICS,
                            CONVERSION_METRICS,
                            LOW_QUALITY_METRICS,
                            REVENUE_METRICS,
                            ("ImpressionSharePercent",),
                        ),
                        primary_key=unique(COMMON_PRIMARY_KEY,),
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            COMMON_PRIMARY_KEY,
                            COMMON_PERFORMANCE_METRICS,
                            AVERAGE_METRICS,
                            CONVERSION_METRICS,
                            LOW_QUALITY_METRICS,
                            REVENUE_METRICS,
                        ),
                        primary_key=unique(COMMON_PRIMARY_KEY,),
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
                            RESTRICTING_PERFORMANCE_METRICS,
                            HISTORICAL_METRICS,
                        ),
                        primary_key=AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            AD_GROUP_PERFORMANCE_COMMON_COLUMNS,
                            RESTRICTING_PERFORMANCE_METRICS,
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
                            HISTORICAL_METRICS,
                        ),
                        primary_key=CAMPAIGN_PERFORMANCE_RESTRICTED_PRIMARY_KEY,
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=CAMPAIGN_PERFORMANCE_COMMON_COLUMNS,
                        primary_key=CAMPAIGN_PERFORMANCE_RESTRICTED_PRIMARY_KEY,
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


if __name__ == "__main__":
    import json
    with open("data/prebuilt_config_preset_names.json", 'w') as out_f:
        json.dump(list(PREBUILT_CONFIGS.keys()), out_f)
