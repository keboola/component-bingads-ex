from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Literal, TypeVar

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
    "TimePeriod",
    "CurrencyCode",
    "AdDistribution",
    "DeviceType",
    "Network",
)

ACCOUNT_AND_CAMPAIGN_PRIMARY_KEY = unique(
    COMMON_PRIMARY_KEY,
    ("AccountId",),
)

ACCOUNT_NAME_PRIMARY_KEY = ("AccountName",)

TOP_VS_OTHER_PRIMARY_KEY = ("TopVsOther",)

RESTRICTED_PRIMARY_KEY = unique(
    (
        "BidMatchType",
        "DeviceOS",
        "Goal",
        "GoalType",
    ),
    TOP_VS_OTHER_PRIMARY_KEY,
)

AD_PRIMARY_KEY = ("AdId",)

AD_GROUP_PRIMARY_KEY = ("AdGroupId",)

CAMPAIGN_PRIMARY_KEY = ("CampaignId",)

LANGUAGE_PRIMARY_KEY = ("Language",)

PRODUCT_DIMENSION_PRIMARY_KEY = unique(
    COMMON_PRIMARY_KEY,
    CAMPAIGN_PRIMARY_KEY,
    AD_GROUP_PRIMARY_KEY,
    AD_PRIMARY_KEY,
    LANGUAGE_PRIMARY_KEY,
    TOP_VS_OTHER_PRIMARY_KEY,
    (
        "MerchantProductId",
        "Condition",
        "Price",
        "ClickTypeId",
        "BidStrategyType",
        "StoreId",
    ),
)

GEOGRAPHIC_PRIMARY_KEY = (
    "LocationType",
    "Country",
    "State",
    "County",
    "MetroArea",
    "City",
    "Neighborhood",
    "MostSpecificLocation",
    "LocationId",
    "ProximityTargetLocation",
)

CAMPAIGN_COLUMNS = (
    "CampaignStatus",
    "CustomParameters",
)

BUDGET_COLUMNS = (
    "BudgetName",
    "BudgetStatus",
    "BudgetAssociationStatus",
)

AVERAGE_COST_METRICS = (
    "AverageCpc",
    "AverageCpm",
)

ALL_AVERAGE_METRICS = unique(
    AVERAGE_COST_METRICS,
    ("AveragePosition",),
)

CONVERSION_METRICS = (
    # "Conversions",
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

COMMON_REVENUE_METRICS = (
    "Revenue",
    "RevenuePerConversion",
)

ACCOUNT_AND_CAMPAIGN_REVENUE_METRICS = unique(
    COMMON_REVENUE_METRICS,
    ("RevenuePerAssist",),
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

ASSISTED_METRICS = (
    "AssistedImpressions",
    "AssistedClicks",
)

COMMON_PERFORMANCE_METRICS = (
    "Impressions",
    "Clicks",
    "Ctr",
    "Spend",
    "ReturnOnAdSpend",
    "AllConversionsQualified",
    "ViewThroughConversionsQualified",
)

ACCOUNT_AND_CAMPAIGN_PERFORMANCE_METRICS = unique(
    COMMON_PERFORMANCE_METRICS,
    (
        "PhoneImpressions",
        "PhoneCalls",
        "CostPerConversion",
        "Ptr",
        "Assists",
        "CostPerAssist",
    ),
)

GEOGRAPHIC_PERFORMANCE_METRICS = unique(
    COMMON_PERFORMANCE_METRICS,
    (
        "Radius",
        "CostPerConversion",
        "CostPerAssist",
        "Assists",
    ),
    CONVERSION_METRICS,
)

DAILY_RESTRICTING_PERFORMANCE_METRICS = (
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

CUSTOM_LABEL_COLUMNS = tuple(f"CustomLabel{i}" for i in range(5))

PRODUCT_CATEGORY_COLUMNS = tuple(f"ProductCategory{i}" for i in range(1, 6))

PRODUCT_TYPE_COLUMNS = tuple(f"ProductType{i}" for i in range(1, 6))

ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY = unique(
    ACCOUNT_AND_CAMPAIGN_PRIMARY_KEY,
    ("DeliveredMatchType",),
)

ACCOUNT_PERFORMANCE_COLUMNS_AND_PK = ColumnsAndPrimaryKey(
    columns=unique(
        ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
        RESTRICTED_PRIMARY_KEY,
        ACCOUNT_AND_CAMPAIGN_PERFORMANCE_METRICS,
        ALL_AVERAGE_METRICS,
        CONVERSION_METRICS,
        LOW_QUALITY_METRICS,
        ACCOUNT_AND_CAMPAIGN_REVENUE_METRICS,
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
    ACCOUNT_AND_CAMPAIGN_PERFORMANCE_METRICS,
    ALL_REVENUE_METRICS,
    ALL_AVERAGE_METRICS,
    CONVERSION_METRICS,
    LOW_QUALITY_METRICS,
    ACCOUNT_AND_CAMPAIGN_REVENUE_METRICS,
)

AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY = unique(
    CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
    AD_GROUP_PRIMARY_KEY,
    LANGUAGE_PRIMARY_KEY,
)

AD_GROUP_PERFORMANCE_COMMON_COLUMNS = unique(
    AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
    ACCOUNT_AND_CAMPAIGN_PERFORMANCE_METRICS,
    CAMPAIGN_METRICS,
    CAMPAIGN_COLUMNS,
    ("FinalUrlSuffix",),
    ALL_REVENUE_METRICS,
    ALL_AVERAGE_METRICS,
    CONVERSION_METRICS,
    ACCOUNT_AND_CAMPAIGN_REVENUE_METRICS,
)

AD_GROUP_PERFORMANCE_RESTRICTED_PRIMARY_KEY = unique(
    AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
    RESTRICTED_PRIMARY_KEY,
)

PRODUCT_DIMENSION_PERFORMANCE_COLUMNS_AND_PK = ColumnsAndPrimaryKey(
    columns=unique(
        PRODUCT_DIMENSION_PRIMARY_KEY,
        (
            "Brand",
            "LocalStoreCode",
            "ClickType",
            "Title",
            "SellerName",
            "OfferLanguage",
            "CountryOfSale",
            "TotalClicksOnAdElements",
        ),
        CUSTOM_LABEL_COLUMNS,
        PRODUCT_CATEGORY_COLUMNS,
        PRODUCT_TYPE_COLUMNS,
        COMMON_PERFORMANCE_METRICS,
        CONVERSION_METRICS,
        COMMON_REVENUE_METRICS,
        ASSISTED_METRICS,
        AVERAGE_COST_METRICS,
    ),
    primary_key=unique(PRODUCT_DIMENSION_PRIMARY_KEY, ),
)

GEOGRAPHIC_PERFORMANCE_COLUMNS_AND_PK = ColumnsAndPrimaryKey(
    columns=unique(
        CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
        ACCOUNT_NAME_PRIMARY_KEY,
        RESTRICTED_PRIMARY_KEY,
        GEOGRAPHIC_PRIMARY_KEY,
        GEOGRAPHIC_PERFORMANCE_METRICS,
    ),
    primary_key=unique(
        CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
        RESTRICTED_PRIMARY_KEY,
        GEOGRAPHIC_PRIMARY_KEY,
    ),
)

# Add AccountName as column and PK to AccountPerformance
ACCOUNT_PERFORMANCE_COLUMNS_AND_PK.columns.insert(6, "AccountName")

# Add AccountName as column and PK to AccountImpressionPerformance
ACCOUNT_AND_CAMPAIGN_PERFORMANCE_COLS_WITH_NAMES = ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY.copy()
ACCOUNT_AND_CAMPAIGN_PERFORMANCE_COLS_WITH_NAMES.insert(6, "AccountName")

# Add AccountName, CampaignName and AdGroupName to AdGroupPerformance, AdGroupImpressionPerformance
AD_GROUP_PERFORMANCE_COMMON_COLUMNS.insert(6, "AccountName")
AD_GROUP_PERFORMANCE_COMMON_COLUMNS.insert(9, "CampaignName")
AD_GROUP_PERFORMANCE_COMMON_COLUMNS.insert(11, "AdGroupName")

# Add AccountName, CampaignName and AdGroupName to CampaignPerformance and CampaignImpressionPerformance
CAMPAIGN_PERFORMANCE_COMMON_COLUMNS.insert(6, "AccountName")
CAMPAIGN_PERFORMANCE_COMMON_COLUMNS.insert(9, "CampaignName")

# Add AdGroupName, CampaignName to ProductDimensionPerformance
PRODUCT_DIMENSION_PERFORMANCE_COLUMNS_AND_PK.columns.insert(6, "CampaignName")
PRODUCT_DIMENSION_PERFORMANCE_COLUMNS_AND_PK.columns.insert(8, "AdGroupName")

# Add CampaignName to GeographicPerformance
GEOGRAPHIC_PERFORMANCE_COLUMNS_AND_PK.columns.insert(8, "CampaignName")

PREBUILT_CONFIGS = {
    "AccountPerformance":
        PrebuiltReportConfig(
            report_type="AccountPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily": ColumnsAndPrimaryKey(
                    columns=ACCOUNT_PERFORMANCE_COLUMNS_AND_PK.columns,
                    primary_key=ACCOUNT_PERFORMANCE_COLUMNS_AND_PK.primary_key
                ),
                "Hourly": ColumnsAndPrimaryKey(
                    columns=ACCOUNT_PERFORMANCE_COLUMNS_AND_PK.columns,
                    primary_key=ACCOUNT_PERFORMANCE_COLUMNS_AND_PK.primary_key),
            },
        ),
    "AccountImpressionPerformance":
        PrebuiltReportConfig(
            report_type="AccountPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            ACCOUNT_AND_CAMPAIGN_PERFORMANCE_COLS_WITH_NAMES,
                            ACCOUNT_AND_CAMPAIGN_PERFORMANCE_METRICS,
                            DAILY_RESTRICTING_PERFORMANCE_METRICS,
                            ALL_AVERAGE_METRICS,
                            CONVERSION_METRICS,
                            LOW_QUALITY_METRICS,
                            ACCOUNT_AND_CAMPAIGN_REVENUE_METRICS,
                            IMPRESSION_METRICS,
                            check_already_unique=False,
                        ),
                        primary_key=ACCOUNT_AND_CAMPAIGN_PERFORMANCE_PRIMARY_KEY,
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(
                            ACCOUNT_AND_CAMPAIGN_PERFORMANCE_COLS_WITH_NAMES,
                            ACCOUNT_AND_CAMPAIGN_PERFORMANCE_METRICS,
                            ALL_AVERAGE_METRICS,
                            CONVERSION_METRICS,
                            LOW_QUALITY_METRICS,
                            ACCOUNT_AND_CAMPAIGN_REVENUE_METRICS,
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
                            DAILY_RESTRICTING_PERFORMANCE_METRICS,
                            IMPRESSION_METRICS,
                            HISTORICAL_METRICS,
                            check_already_unique=False,
                        ),
                        primary_key=AD_GROUP_PERFORMANCE_COMMON_PRIMARY_KEY,
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(AD_GROUP_PERFORMANCE_COMMON_COLUMNS, ),
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
                            DAILY_RESTRICTING_PERFORMANCE_METRICS,
                            IMPRESSION_METRICS,
                            HISTORICAL_METRICS,
                            check_already_unique=False,
                        ),
                        primary_key=CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=unique(CAMPAIGN_PERFORMANCE_COMMON_COLUMNS, ),
                        primary_key=CAMPAIGN_PERFORMANCE_COMMON_PRIMARY_KEY,
                    ),
            },
        ),
    "ProductDimensionPerformance":
        PrebuiltReportConfig(
            report_type="ProductDimensionPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily": PRODUCT_DIMENSION_PERFORMANCE_COLUMNS_AND_PK,
                "Hourly": PRODUCT_DIMENSION_PERFORMANCE_COLUMNS_AND_PK,
            },
        ),
    "KeywordPerformance":
        PrebuiltReportConfig(
            report_type="KeywordPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily":
                    ColumnsAndPrimaryKey(
                        columns=[
                            "AccountId", "AccountName", "CampaignId", "CampaignName", "AdGroupId", "AdGroupName",
                            "KeywordId", "Keyword", "AdId", "TimePeriod", "CurrencyCode",
                            "DeliveredMatchType", "AdDistribution", "DeviceType", "Language", "Network", "DeviceOS",
                            "TopVsOther", "BidMatchType", "KeywordStatus", "Impressions", "Clicks", "Ctr",
                            "CurrentMaxCpc", "AverageCpc", "Spend", "AveragePosition", "Conversions",
                            "ConversionsQualified", "ConversionRate", "CostPerConversion", "QualityScore",
                            "ExpectedCtr", "AdRelevance", "LandingPageExperience", "QualityImpact", "Assists",
                            "ReturnOnAdSpend", "CostPerAssist", "CustomParameters", "FinalAppUrl", "Mainline1Bid",
                            "MainlineBid", "FirstPageBid", "FinalUrlSuffix", "ViewThroughConversions",
                            "ViewThroughConversionsQualified", "AllCostPerConversion", "AllReturnOnAdSpend",
                            "AllConversionsQualified", "AllRevenue", "AllRevenuePerConversion", "HistoricalAdRelevance",
                            "HistoricalExpectedCtr", "HistoricalLandingPageExperience", "HistoricalQualityScore",
                            "Revenue", "RevenuePerAssist", "RevenuePerConversion"
                        ],
                        primary_key=[
                            "AccountId", "CampaignId", "AdGroupId", "KeywordId", "AdId", "TimePeriod", "CurrencyCode",
                            "DeliveredMatchType", "AdDistribution", "DeviceType", "Language", "Network", "DeviceOS",
                            "TopVsOther", "BidMatchType"
                        ],
                    ),
                "Hourly":
                    ColumnsAndPrimaryKey(
                        columns=[
                            "AccountId", "AccountName", "CampaignId", "CampaignName", "AdGroupId", "AdGroupName",
                            "KeywordId", "Keyword", "AdId", "TimePeriod", "CurrencyCode",
                            "DeliveredMatchType", "AdDistribution", "DeviceType", "Language", "Network", "DeviceOS",
                            "TopVsOther", "BidMatchType", "KeywordStatus", "Impressions", "Clicks", "Ctr",
                            "CurrentMaxCpc", "AverageCpc", "Spend", "AveragePosition", "Conversions", "ConversionRate",
                            "CostPerConversion", "QualityScore", "ExpectedCtr", "AdRelevance", "LandingPageExperience",
                            "QualityImpact", "Assists", "ReturnOnAdSpend", "CostPerAssist", "CustomParameters",
                            "FinalAppUrl", "FinalUrlSuffix", "Mainline1Bid", "MainlineBid", "FirstPageBid",
                            "ViewThroughConversions", "AllCostPerConversion", "AllReturnOnAdSpend",
                            "AllConversionsQualified", "AllRevenue", "AllRevenuePerConversion", "Revenue",
                            "RevenuePerAssist", "RevenuePerConversion"
                        ],
                        primary_key=[
                            "AccountId", "CampaignId", "AdGroupId", "KeywordId", "AdId", "TimePeriod", "CurrencyCode",
                            "DeliveredMatchType", "AdDistribution", "DeviceType", "Language", "Network", "DeviceOS",
                            "TopVsOther", "BidMatchType"
                        ],
                    ),
            },
        ),
    "GeographicPerformance":
        PrebuiltReportConfig(
            report_type="GeographicPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily": GEOGRAPHIC_PERFORMANCE_COLUMNS_AND_PK,
                "Hourly": GEOGRAPHIC_PERFORMANCE_COLUMNS_AND_PK,
            },
        ),
    "AssetPerformance":
        PrebuiltReportConfig(
            report_type="AssetPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily": ColumnsAndPrimaryKey(
                    columns=[
                        "AccountId",
                        "AccountName",
                        "AdGroupId",
                        "AdGroupName",
                        "AssetContent",
                        "AssetId",
                        "AssetSource",
                        "AssetType",
                        "CampaignId",
                        "CampaignName",
                        "Clicks",
                        "CompletedVideoViews",
                        "Conversions",
                        "Ctr",
                        "Impressions",
                        "Revenue",
                        "Spend",
                        "TimePeriod",
                        "VideoCompletionRate",
                        "VideoViews",
                        "VideoViewsAt25Percent",
                        "VideoViewsAt50Percent",
                        "VideoViewsAt75Percent"
                    ],
                    primary_key=[
                        "AccountId",
                        "AccountName",
                        "AdGroupId",
                        "AdGroupName",
                        "AssetContent",
                        "AssetId",
                        "AssetSource",
                        "AssetType",
                        "CampaignId",
                        "CampaignName",
                        "TimePeriod"
                    ]
                ),
                "Hourly": ColumnsAndPrimaryKey(
                    columns=[
                        "AccountId",
                        "AccountName",
                        "AdGroupId",
                        "AdGroupName",
                        "AssetContent",
                        "AssetId",
                        "AssetSource",
                        "AssetType",
                        "CampaignId",
                        "CampaignName",
                        "Clicks",
                        "CompletedVideoViews",
                        "Conversions",
                        "Ctr",
                        "Impressions",
                        "Revenue",
                        "Spend",
                        "TimePeriod",
                        "VideoCompletionRate",
                        "VideoViews",
                        "VideoViewsAt25Percent",
                        "VideoViewsAt50Percent",
                        "VideoViewsAt75Percent"
                    ],
                    primary_key=[
                        "AccountId",
                        "AccountName",
                        "AdGroupId",
                        "AdGroupName",
                        "AssetContent",
                        "AssetId",
                        "AssetSource",
                        "AssetType",
                        "CampaignId",
                        "CampaignName",
                        "TimePeriod"
                    ]
                ),
            },
        ),
    "AssetGroupPerformance":
        PrebuiltReportConfig(
            report_type="AssetGroupPerformance",
            columns_and_primary_key_by_aggregation={
                "Daily": ColumnsAndPrimaryKey(
                    columns=[
                        "AccountId",
                        "AccountName",
                        "AccountStatus",
                        "AssetGroupId",
                        "AssetGroupName",
                        "AssetGroupStatus",
                        "AverageCpc",
                        "CampaignId",
                        "CampaignName",
                        "CampaignStatus",
                        "CampaignType",
                        "Clicks",
                        "Conversions",
                        "Ctr",
                        "Impressions",
                        "ReturnOnAdSpend",
                        "Revenue",
                        "Spend",
                        "TimePeriod"
                    ],
                    primary_key=[
                        "AccountId",
                        "AccountName",
                        "AccountStatus",
                        "AssetGroupId",
                        "AssetGroupName",
                        "AssetGroupStatus",
                        "CampaignId",
                        "CampaignName",
                        "CampaignStatus",
                        "CampaignType",
                        "TimePeriod"
                    ]
                ),
                "Hourly": ColumnsAndPrimaryKey(
                    columns=[
                        "AccountId",
                        "AccountName",
                        "AccountStatus",
                        "AssetGroupId",
                        "AssetGroupName",
                        "AssetGroupStatus",
                        "AverageCpc",
                        "CampaignId",
                        "CampaignName",
                        "CampaignStatus",
                        "CampaignType",
                        "Clicks",
                        "Conversions",
                        "Ctr",
                        "Impressions",
                        "ReturnOnAdSpend",
                        "Revenue",
                        "Spend",
                        "TimePeriod"
                    ],
                    primary_key=[
                        "AccountId",
                        "AccountName",
                        "AccountStatus",
                        "AssetGroupId",
                        "AssetGroupName",
                        "AssetGroupStatus",
                        "CampaignId",
                        "CampaignName",
                        "CampaignStatus",
                        "CampaignType",
                        "TimePeriod"
                    ]
                ),
            },
        )
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
    reference_presets: dict[str, dict[str, dict[str, list[str]]]] = json.loads(reference_presets_path.read_text())

    def compare_prebuilt_config_to_reference(config_name: str, config: PrebuiltReportConfig):
        reference_preset = reference_presets.get(config_name)
        if not reference_preset:
            return config_name, {"Error": "No reference report."}
        report = dict()
        for aggregation in config.columns_and_primary_key_by_aggregation.keys():
            reference_columns_and_primary_key = ColumnsAndPrimaryKey(
                columns=reference_preset[aggregation]["columns"],
                primary_key=reference_preset[aggregation]["primary_key"])
            reference_columns = reference_columns_and_primary_key.columns
            reference_primary_key = reference_columns_and_primary_key.primary_key
            config_columns_and_primary_key = config.columns_and_primary_key_by_aggregation[aggregation]
            config_columns = config_columns_and_primary_key.columns
            config_primary_key = config_columns_and_primary_key.primary_key
            missing_columns = [col for col in reference_columns if col not in config_columns]
            extra_columns = [col for col in config_columns if col not in reference_columns]
            missing_primary_key = [col for col in reference_primary_key if col not in config_primary_key]
            extra_primary_key = [col for col in config_primary_key if col not in reference_primary_key]
            report[aggregation] = {
                "missing_columns": missing_columns,
                "extra_columns": extra_columns,
                "missing_primary_key": missing_primary_key,
                "extra_primary_key": extra_primary_key
            }
        return config_name, report

    reference_comparison_report = {
        config_name: report for config_name, report in (compare_prebuilt_config_to_reference(config_name, config)
                                                        for config_name, config in PREBUILT_CONFIGS.items())
    }
    with open("data/reference_comparison_report.json", 'w') as out_f:
        json.dump(reference_comparison_report, out_f)

    def create_prebuilt_config_markdown_fragment(config_name: str, config: PrebuiltReportConfig):
        fragment = f"## {config_name} Report Presets"
        for aggregation, columns_and_pk in config.columns_and_primary_key_by_aggregation.items():
            column_str = ", ".join(columns_and_pk.columns)
            pk_str = ", ".join(columns_and_pk.primary_key)
            agg_fragment = (f"\n### {aggregation} aggregation"
                            f"\n\n#### Columns\n```{column_str}```\n\n#### Primary key\n```{pk_str}```")
            fragment += agg_fragment
        return fragment

    header_section = "# Columns and primary key of report configuration presets\n\n **Table of contents:** \n\n[TOC] \n"
    report_presets_markdown = (header_section + "\n\n".join(
        create_prebuilt_config_markdown_fragment(config_name, config)
        for config_name, config in PREBUILT_CONFIGS.items()))
    with open("docs/report_presets_columns_and_pk.md", 'w') as out_f:
        out_f.write(report_presets_markdown)
