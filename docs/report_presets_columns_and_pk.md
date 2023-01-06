# Columns and primary key of report configuration presets
## AccountPerformance Report Presets
### Daily aggregation
#### Columns
<<<<<<< HEAD
<<<<<<< HEAD
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther```
### Hourly aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther```
## AccountImpressionPerformance Report Presets
### Daily aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AbsoluteTopImpressionRatePercent, AbsoluteTopImpressionShareLostToBudgetPercent, AbsoluteTopImpressionShareLostToRankPercent, AbsoluteTopImpressionSharePercent, ClickSharePercent, ExactMatchImpressionSharePercent, ImpressionLostToBudgetPercent, ImpressionLostToRankAggPercent, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, ImpressionSharePercent```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType```
### Hourly aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType```
=======
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, AccountName`
=======
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist`
>>>>>>> 55fbd42 (change columns placement in documentation)
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther`
### Hourly aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther`
## AccountImpressionPerformance Report Presets
### Daily aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AbsoluteTopImpressionRatePercent, AbsoluteTopImpressionShareLostToBudgetPercent, AbsoluteTopImpressionShareLostToRankPercent, AbsoluteTopImpressionSharePercent, ClickSharePercent, ExactMatchImpressionSharePercent, ImpressionLostToBudgetPercent, ImpressionLostToRankAggPercent, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, ImpressionSharePercent`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType`
### Hourly aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist`
#### Primary key
<<<<<<< HEAD
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, AccountName`
>>>>>>> 5da899f (add AccountName to AccountImpressionPerformance report)
## AdGroupPerformance Report Presets
### Daily aggregation
#### Columns
<<<<<<< HEAD
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther```
=======
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore, AccountName, CampaignName, AdGroupName`
#### Primary key
<<<<<<< HEAD
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, BidMatchType, DeviceOS, Goal, GoalType, TopVsOtherAccountName, CampaignName, AdGroupName`
>>>>>>> 892b846 (add new columns with names)
=======
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, AccountName, CampaignName, AdGroupName`
>>>>>>> a1e14c2 (fix typo in docu)
### Hourly aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther```
=======
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType`
## AdGroupPerformance Report Presets
### Daily aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, AdGroupId, AdGroupName, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther`
### Hourly aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, AdGroupId, AdGroupName, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther`
>>>>>>> 55fbd42 (change columns placement in documentation)
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther```
## AdGroupImpressionPerformance Report Presets
### Daily aggregation
#### Columns
<<<<<<< HEAD
<<<<<<< HEAD
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist, AbsoluteTopImpressionRatePercent, AbsoluteTopImpressionShareLostToBudgetPercent, AbsoluteTopImpressionShareLostToRankPercent, AbsoluteTopImpressionSharePercent, ClickSharePercent, ExactMatchImpressionSharePercent, ImpressionLostToBudgetPercent, ImpressionLostToRankAggPercent, ImpressionSharePercent, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language```
### Hourly aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language```
## CampaignPerformance Report Presets
### Daily aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, CampaignStatus, CustomParameters, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, BudgetName, BudgetStatus, BudgetAssociationStatus, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther```
### Hourly aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, CampaignStatus, CustomParameters, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, BudgetName, BudgetStatus, BudgetAssociationStatus```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther```
## CampaignImpressionPerformance Report Presets
### Daily aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, CampaignStatus, CustomParameters, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, AbsoluteTopImpressionRatePercent, AbsoluteTopImpressionShareLostToBudgetPercent, AbsoluteTopImpressionShareLostToRankPercent, AbsoluteTopImpressionSharePercent, ClickSharePercent, ExactMatchImpressionSharePercent, ImpressionLostToBudgetPercent, ImpressionLostToRankAggPercent, ImpressionSharePercent, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId```
### Hourly aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, CampaignStatus, CustomParameters, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId```
## ProductDimensionPerformance Report Presets
### Daily aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, CampaignId, AdGroupId, AdId, Language, TopVsOther, MerchantProductId, Condition, Price, ClickTypeId, BidStrategyType, StoreId, Brand, LocalStoreCode, ClickType, Title, SellerName, OfferLanguage, CountryOfSale, TotalClicksOnAdElements, CustomLabel0, CustomLabel1, CustomLabel2, CustomLabel3, CustomLabel4, ProductCategory1, ProductCategory2, ProductCategory3, ProductCategory4, ProductCategory5, ProductType1, ProductType2, ProductType3, ProductType4, ProductType5, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, AssistedImpressions, AssistedClicks, AverageCpc, AverageCpm```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, CampaignId, AdGroupId, AdId, Language, TopVsOther, MerchantProductId, Condition, Price, ClickTypeId, BidStrategyType, StoreId```
### Hourly aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, CampaignId, AdGroupId, AdId, Language, TopVsOther, MerchantProductId, Condition, Price, ClickTypeId, BidStrategyType, StoreId, Brand, LocalStoreCode, ClickType, Title, SellerName, OfferLanguage, CountryOfSale, TotalClicksOnAdElements, CustomLabel0, CustomLabel1, CustomLabel2, CustomLabel3, CustomLabel4, ProductCategory1, ProductCategory2, ProductCategory3, ProductCategory4, ProductCategory5, ProductType1, ProductType2, ProductType3, ProductType4, ProductType5, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, AssistedImpressions, AssistedClicks, AverageCpc, AverageCpm```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, CampaignId, AdGroupId, AdId, Language, TopVsOther, MerchantProductId, Condition, Price, ClickTypeId, BidStrategyType, StoreId```
## KeywordPerformance Report Presets
### Daily aggregation
#### Columns
```AccountId, CampaignId, AdGroupId, KeywordId, AdId, TimePeriod, CurrencyCode, DeliveredMatchType, AdDistribution, DeviceType, Language, Network, DeviceOS, TopVsOther, BidMatchType, KeywordStatus, Impressions, Clicks, Ctr, CurrentMaxCpc, AverageCpc, Spend, AveragePosition, Conversions, ConversionsQualified, ConversionRate, CostPerConversion, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, QualityImpact, Assists, ReturnOnAdSpend, CostPerAssist, CustomParameters, FinalAppUrl, Mainline1Bid, MainlineBid, FirstPageBid, FinalUrlSuffix, ViewThroughConversions, ViewThroughConversionsQualified, AllCostPerConversion, AllReturnOnAdSpend, AllConversionsQualified, AllRevenue, AllRevenuePerConversion, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore, Revenue, RevenuePerAssist, RevenuePerConversion```
#### Primary key
```AccountId, CampaignId, AdGroupId, KeywordId, AdId, TimePeriod, CurrencyCode, DeliveredMatchType, AdDistribution, DeviceType, Language, Network, DeviceOS, TopVsOther, BidMatchType```
### Hourly aggregation
#### Columns
```AccountId, CampaignId, AdGroupId, KeywordId, AdId, TimePeriod, CurrencyCode, DeliveredMatchType, AdDistribution, DeviceType, Language, Network, DeviceOS, TopVsOther, BidMatchType, KeywordStatus, Impressions, Clicks, Ctr, CurrentMaxCpc, AverageCpc, Spend, AveragePosition, Conversions, ConversionRate, CostPerConversion, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, QualityImpact, Assists, ReturnOnAdSpend, CostPerAssist, CustomParameters, FinalAppUrl, FinalUrlSuffix, Mainline1Bid, MainlineBid, FirstPageBid, ViewThroughConversions, AllCostPerConversion, AllReturnOnAdSpend, AllConversionsQualified, AllRevenue, AllRevenuePerConversion, Revenue, RevenuePerAssist, RevenuePerConversion```
#### Primary key
```AccountId, CampaignId, AdGroupId, KeywordId, AdId, TimePeriod, CurrencyCode, DeliveredMatchType, AdDistribution, DeviceType, Language, Network, DeviceOS, TopVsOther, BidMatchType```
## GeographicPerformance Report Presets
### Daily aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AccountName, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, Radius, CostPerConversion, CostPerAssist, Assists, ConversionRate, ConversionsQualified```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation```
### Hourly aggregation
#### Columns
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AccountName, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, Radius, CostPerConversion, CostPerAssist, Assists, ConversionRate, ConversionsQualified```
#### Primary key
```TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation```
=======
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist, AbsoluteTopImpressionRatePercent, AbsoluteTopImpressionShareLostToBudgetPercent, AbsoluteTopImpressionShareLostToRankPercent, AbsoluteTopImpressionSharePercent, ClickSharePercent, ExactMatchImpressionSharePercent, ImpressionLostToBudgetPercent, ImpressionLostToRankAggPercent, ImpressionSharePercent, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore, AccountName, CampaignName, AdGroupName`
=======
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, AdGroupId, AdGroupName, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist, AbsoluteTopImpressionRatePercent, AbsoluteTopImpressionShareLostToBudgetPercent, AbsoluteTopImpressionShareLostToRankPercent, AbsoluteTopImpressionSharePercent, ClickSharePercent, ExactMatchImpressionSharePercent, ImpressionLostToBudgetPercent, ImpressionLostToRankAggPercent, ImpressionSharePercent, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore`
>>>>>>> 55fbd42 (change columns placement in documentation)
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language`
### Hourly aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, AdGroupId, AdGroupName, Language, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, CampaignStatus, CustomParameters, FinalUrlSuffix, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, RevenuePerAssist`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, AdGroupId, Language`
## CampaignPerformance Report Presets
### Daily aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, CampaignStatus, CustomParameters, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, BudgetName, BudgetStatus, BudgetAssociationStatus, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, AccountName, CampaignName`
### Hourly aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, CampaignStatus, CustomParameters, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, BudgetName, BudgetStatus, BudgetAssociationStatus`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther`
## CampaignImpressionPerformance Report Presets
### Daily aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, CampaignStatus, CustomParameters, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist, AbsoluteTopImpressionRatePercent, AbsoluteTopImpressionShareLostToBudgetPercent, AbsoluteTopImpressionShareLostToRankPercent, AbsoluteTopImpressionSharePercent, ClickSharePercent, ExactMatchImpressionSharePercent, ImpressionLostToBudgetPercent, ImpressionLostToRankAggPercent, ImpressionSharePercent, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId`
### Hourly aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, CampaignStatus, CustomParameters, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, PhoneImpressions, PhoneCalls, CostPerConversion, Ptr, Assists, CostPerAssist, AllRevenue, AllRevenuePerConversion, AverageCpc, AverageCpm, AveragePosition, ConversionRate, ConversionsQualified, LowQualityClicks, LowQualityClicksPercent, LowQualityConversionRate, LowQualityConversions, LowQualityConversionsQualified, LowQualityGeneralClicks, LowQualityImpressions, LowQualityImpressionsPercent, LowQualitySophisticatedClicks, Revenue, RevenuePerConversion, RevenuePerAssist`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId`
## ProductDimensionPerformance Report Presets
### Daily aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, CampaignId, CampaignName, AdGroupId, AdGroupName, AdId, Language, TopVsOther, MerchantProductId, Condition, Price, ClickTypeId, BidStrategyType, StoreId, Brand, LocalStoreCode, ClickType, Title, SellerName, OfferLanguage, CountryOfSale, TotalClicksOnAdElements, CustomLabel0, CustomLabel1, CustomLabel2, CustomLabel3, CustomLabel4, ProductCategory1, ProductCategory2, ProductCategory3, ProductCategory4, ProductCategory5, ProductType1, ProductType2, ProductType3, ProductType4, ProductType5, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, AssistedImpressions, AssistedClicks, AverageCpc, AverageCpm`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, CampaignId, AdGroupId, AdId, Language, TopVsOther, MerchantProductId, Condition, Price, ClickTypeId, BidStrategyType, StoreId`
### Hourly aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, CampaignId, CampaignName, AdGroupId, AdGroupName, AdId, Language, TopVsOther, MerchantProductId, Condition, Price, ClickTypeId, BidStrategyType, StoreId, Brand, LocalStoreCode, ClickType, Title, SellerName, OfferLanguage, CountryOfSale, TotalClicksOnAdElements, CustomLabel0, CustomLabel1, CustomLabel2, CustomLabel3, CustomLabel4, ProductCategory1, ProductCategory2, ProductCategory3, ProductCategory4, ProductCategory5, ProductType1, ProductType2, ProductType3, ProductType4, ProductType5, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, ConversionRate, ConversionsQualified, Revenue, RevenuePerConversion, AssistedImpressions, AssistedClicks, AverageCpc, AverageCpm`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, CampaignId, AdGroupId, AdId, Language, TopVsOther, MerchantProductId, Condition, Price, ClickTypeId, BidStrategyType, StoreId`
## KeywordPerformance Report Presets
### Daily aggregation
#### Columns
`AccountId, AccountName, CampaignId, CampaignName, AdGroupId, AdGroupName, KeywordId, Keyword, AdId, TimePeriod, CurrencyCode, DeliveredMatchType, AdDistribution, DeviceType, Language, Network, DeviceOS, TopVsOther, BidMatchType, KeywordStatus, Impressions, Clicks, Ctr, CurrentMaxCpc, AverageCpc, Spend, AveragePosition, Conversions, ConversionsQualified, ConversionRate, CostPerConversion, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, QualityImpact, Assists, ReturnOnAdSpend, CostPerAssist, CustomParameters, FinalAppUrl, Mainline1Bid, MainlineBid, FirstPageBid, FinalUrlSuffix, ViewThroughConversions, ViewThroughConversionsQualified, AllCostPerConversion, AllReturnOnAdSpend, AllConversionsQualified, AllRevenue, AllRevenuePerConversion, HistoricalAdRelevance, HistoricalExpectedCtr, HistoricalLandingPageExperience, HistoricalQualityScore, Revenue, RevenuePerAssist, RevenuePerConversion`
#### Primary key
`AccountId, AccountName, CampaignId, CampaignName, AdGroupId, KeywordId, AdId, TimePeriod, CurrencyCode, DeliveredMatchType, AdDistribution, DeviceType, Language, Network, DeviceOS, TopVsOther, BidMatchType`
### Hourly aggregation
#### Columns
`AccountId, AccountName, CampaignId, CampaignName, AdGroupId, AdGroupName, KeywordId, Keyword, AdId, TimePeriod, CurrencyCode, DeliveredMatchType, AdDistribution, DeviceType, Language, Network, DeviceOS, TopVsOther, BidMatchType, KeywordStatus, Impressions, Clicks, Ctr, CurrentMaxCpc, AverageCpc, Spend, AveragePosition, Conversions, ConversionRate, CostPerConversion, QualityScore, ExpectedCtr, AdRelevance, LandingPageExperience, QualityImpact, Assists, ReturnOnAdSpend, CostPerAssist, CustomParameters, FinalAppUrl, FinalUrlSuffix, Mainline1Bid, MainlineBid, FirstPageBid, ViewThroughConversions, AllCostPerConversion, AllReturnOnAdSpend, AllConversionsQualified, AllRevenue, AllRevenuePerConversion, Revenue, RevenuePerAssist, RevenuePerConversion`
#### Primary key
`AccountId, CampaignId, AdGroupId, KeywordId, AdId, TimePeriod, CurrencyCode, DeliveredMatchType, AdDistribution, DeviceType, Language, Network, DeviceOS, TopVsOther, BidMatchType`
## GeographicPerformance Report Presets
### Daily aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, Radius, CostPerConversion, CostPerAssist, Assists, ConversionRate, ConversionsQualified`
#### Primary key
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation`
### Hourly aggregation
#### Columns
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, AccountName, DeliveredMatchType, CampaignId, CampaignName, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation, Impressions, Clicks, Ctr, Spend, ReturnOnAdSpend, AllConversionsQualified, ViewThroughConversionsQualified, Radius, CostPerConversion, CostPerAssist, Assists, ConversionRate, ConversionsQualified`
#### Primary key
<<<<<<< HEAD
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation, CampaignName`
>>>>>>> 892b846 (add new columns with names)
=======
`TimePeriod, CurrencyCode, AdDistribution, DeviceType, Network, AccountId, DeliveredMatchType, CampaignId, BidMatchType, DeviceOS, Goal, GoalType, TopVsOther, LocationType, Country, State, County, MetroArea, City, Neighborhood, MostSpecificLocation, LocationId, ProximityTargetLocation`
>>>>>>> 55fbd42 (change columns placement in documentation)
