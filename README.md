# Bing Ads Extractor

This data source component supports extracting either campaign entity data or various types of reports available. In
case of reports you can specify your own set of columns and primary key to use in Keboola Storage, but there are also
presets of columns and appropriate primary keys available.

**Table of contents:**

[TOC]

## Prerequisites

1. Find your Bing Ads Account ID and Customer ID. Follow [this part of the official documentation](https://learn.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-ids). Both should be numbers such as `391827251`.

2. Log into your account using the Authorize Account button in the Keboola interface. 

![OAuth Authorization](docs/imgs/config_oauth.png)


## Configuration

### Global configuration
- Customer ID (customer_id) - [REQ] Customer identifier. (See [Prerequisites](#prerequisites) for info on how to find it.)
- Account ID (account_id) - [REQ] Account identifier. (See [Prerequisites](#prerequisites) for info on how to find it.)

### Row configuration

- Object type (object_type) - [REQ] This determines whether you want to extract campaign entities (such as Ads, Ad Groups, Campaigns etc.) or reports, and, if you want to extract reports, whether you want to use one of the presets or your own set of columns and primary key.
- Destination (destination) - [REQ] This part of row configuration determines how the extracted data will be saved in Keboola Storage.
    - Load Type (load_type) - [REQ] If Full load is used, the destination table will be overwritten every run. If Incremental Load is used, data will be upserted into the destination table.
    - Storage Table Name (output_table_name) - [REQ] Name of the table stored in Storage. Default object name used if left empty.

Rest of the configuration depends on what Object Type is selected:

- Entity Settings (bulk_settings) - [OPT] This part of row configuration only becomes available if `Entity` is selected as the Object Type.
    - Entities (download_entities) - [REQ] Comma separated list of entities (or rather entity types) to download, find supported entities in the [official documentation](https://learn.microsoft.com/en-us/advertising/bulk-service/downloadentity?view=bingads-13#values). Currently only the extraction of entities within the `EntityData` data scope is supported.
    - Only download changes since the last run (since_last_sync_time) - [REQ] If checked, only changes since the last component run will be downloaded. If checked for the first run of this component row, it will be ignored (i.e. all data will be downloaded).
- Report Settings Custom (report_settings_custom) - [OPT] This part of row configuration only becomes available if `Report (Custom)` is selected as the Object Type.
    - Report type (report_type) - [REQ] Select one of the available report types described in the [official documentation](https://learn.microsoft.com/en-us/advertising/guides/report-types?view=bingads-13).
    - Report Aggregation (aggregation) - [REQ] The type of aggregation to use to aggregate the report data.
    - Time Range (time_range) - [REQ] Settings determining what time period the report should be about.
        - Report Time Zone (time_zone) - [REQ] Determines the time zone that is used to establish today's date.
        - Report Period (period) - [REQ] The time period the report should be about. If `CustomTimeRange` you will also need to provide the next 2 parameters:
        - Date From (date_from) - [OPT] Start date of the report. Either date in YYYY-MM-DD format or a relative date string i.e. 5 days ago, 1 month ago, yesterday, etc. Can also be specified as `last run` to start the reporting period at the time of last extraction (this cannot be done in case of the first run for obvious reasons).
        - Date To (date_to) - [OPT] End date of the report. Either date in YYYY-MM-DD format or relative date string i.e. 5 days ago, 1 month ago, yesterday, etc.
    - Return only complete data (return_only_complete_data) - [REQ] Determines whether or not the service must ensure that all the data has been processed and is available. If checked, and the requested data are (partially) incomplete or unavailable, an error will be raised.
    - Columns (columns) - [REQ] Comma separated list of columns to use for the report. For your convenience, available columns for each report type are listed in the appropriate format in [this markdown file inside this git repository](docs/reports_available_columns.md).
    - Primary Key Columns (primary_key) - [REQ] Comma separated list of columns to be used as primary key. For your convenience, available columns for each report type are listed in the appropriate format in [this markdown file inside this git repository](docs/reports_available_columns.md).
- Report Settings Prebuilt (report_settings_prebuilt) - [OPT] This part of row configuration only becomes available if `Report (Prebuilt)` is selected as the Object Type.
    - Preset Name (preset_name) - [REQ] Select one of the available report presets. The columns and primary key that will be used for each preset are described in [this markdown file inside this git repository](docs/report_presets_columns_and_pk.md).
    - Report Aggregation (aggregation) - [REQ] The type of aggregation to use to aggregate the report data. For prebuilt report presets, only Daily and Hourly aggregation is available.
    - Time Range (time_range) - [REQ] Settings determining what time period the report should be about.
        - Report Time Zone (time_zone) - [REQ] Determines the time zone that is used to establish today's date.
        - Report Period (period) - [REQ] The time period the report should be about. If `CustomTimeRange` you will also need to provide the next 2 parameters:
        - Date From (date_from) - [OPT] Start date of the report. Either date in YYYY-MM-DD format or a relative date string i.e. 5 days ago, 1 month ago, yesterday, etc. Can also be specified as `last run` to start the reporting period at the time of last extraction (this cannot be done in case of the first run for obvious reasons).
        - Date To (date_to) - [OPT] End date of the report. Either date in YYYY-MM-DD format or relative date string i.e. 5 days ago, 1 month ago, yesterday, etc.
    - Return only complete data (return_only_complete_data) - [REQ] Determines whether or not the service must ensure that all the data has been processed and is available. If checked, and the requested data are (partially) incomplete or unavailable, an error will be raised.
        

### Sample Configuration
This sample configuration will download an AdGroupPerformance report with [the preset columns and primary key](docs/report_presets_columns_and_pk.md#adgroupperformance-report-presets) and upsert the data into a table called `prebuilt_AdGroupPerformance_ThisYear_Daily`.
```json
{
    "parameters": {
        "authorization": {
            "#developer_token": "THIS IS OPTIONAL USUALLY GET FROM THE PLATFORM IMAGE PARAMETERS",
            "customer_id": 313617589,
            "account_id": 391827251
        },
        "object_type": "report_prebuilt",
        "report_settings_prebuilt": {
            "preset_name": "AdGroupPerformance",
            "aggregation": "Daily",
            "time_range": {
                "time_zone": "BelgradeBratislavaBudapestLjubljanaPrague",
                "period": "ThisYear"
            },
            "return_only_complete_data": false
        },
        "destination": {
            "load_type": "incremental_load",
            "output_table_name": "prebuilt_AdGroupPerformance_ThisYear_Daily"
        }
    }
}
```

## Output
The output of every configuration row is always a single table in the Keboola Storage. If you specify the Storage Table Name in the [row configuration](#row-configuration), this name is used, otherwise a default name is generated as specified below.


### Entities
When extracting campaign entity data (i. e. when Object Type in row config is set to `Entity`), the default name of the Keboola Storage output table is `entities`. The schema of the output table is rather complicated (418 columns), since all possible entity fields need to be covered. It therefore is rather sparse (most values are empty because they do not apply to the entity type of any given row).

### Reports
#### Custom
When extracting report data (i. e. when Object Type in row config is set to `Report (Custom)`), the output table schema depends on the columns set in the Columns parameter. The default table name is constructed as `{report_type}_Report.csv`, where `{report_type}` is the Report Type parameter value specified in the row configuration.
#### Prebuilt
When extracting report data (i. e. when Object Type in row config is set to `Report (Prebuilt)`), the output table schema depends on which report preset specified in the Preset Name row configuration parameter and the chosen aggregation in the Aggregation parameter. You can see what columns are extracted for each combination of Preset Name and Aggregation in [this markdown file inside this git repository](docs/report_presets_columns_and_pk.md). The default table name is constructed as `{preset_name}_{aggregation}_Report.csv`, where `{preset_name}` is the Preset Name parameter value and `{aggregation}` is the value of the Aggregation parameter.


## Development

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path in
the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### Column List Docs Generation
Two markdown files linked above are automatically generated by Python scripts contained in this repository. The [report preset markdown](docs/report_presets_columns_and_pk.md) document is generated by running the [bingads_wrapper/prebuilt_configs.py module](src/bingads_wrapper/prebuilt_configs.py) as a standalone script (for example by this shell command: `python src/bingads_wrapper/prebuilt_configs.py`), and the [available report columns markdown](docs/reports_available_columns.md) is generated by running the [create_all_possible_report_columns_md.py script](scripts/create_all_possible_report_columns_md.py) (for example by this shell command: `python scripts/create_all_possible_report_columns_md.py`).

## Integration

For information about deployment and integration with KBC, please refer to the
[deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/)