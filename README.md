# Netherlands Immigration Panel

This repository builds a monthly panel dataset of immigration to the Netherlands and corresponding economic indicators for six European origin countries: Bulgaria, Germany, Italy, Poland, Romania, and Spain.

The dataset combines immigration observations from Statistics Netherlands (CBS), economic indicators from Eurostat, and the Dutch Conjunctuurklok business-cycle indicator. Additional economic features are engineered to capture changes over time and differences between origin countries and the Netherlands.

The resulting dataset supports the forecasting analysis conducted in the [nl-immigration-thesis](https://github.com/ben-mikus/nl-immigration-thesis) project.


## Setup

Use Python 3.12 or later. From the repository root, create a critual environment and install the dependencies:

```PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Execute the complete pipeline using:

```Powershell
python main.py
```

The pipeline retrieves CBS and Eurostat data at runtime and writes the final
panel to `data\panel_data.csv`. It does not persist raw API responses.


## Configuration

The configuration of the project is separated into two modules:
- **settings.py** controls the contents of the final datset and operational functionality.
- **config.py** defines the API sources, source-specific parameters, country mapping, file paths, and period boundaries.

### User Settings

By default, the configuration includes all six countries, four Eurotat indicators, the Conjunctuurklok featre, and feature engineering. Users can customize the panel data by altering the following:

| Setting | Description |
| --- | --- |
| `COUNTRIES` | Selects the countries included in the output. |
| `METRICS` | Selects which configured Eurostat indicators are retrieved. |
| `CONJUNCTUURKLOK` | Enables or disables the Dutch business-cycle indicator. |
| `FEATURE_ENGINEERING` | Enables or disables the creation of derived economic features. |
| `FEATURE_PERIODS` | Specifies the number of monthly observations used to calculate changes and growth rates. |
| `DEBUG` | Enables detailed diagnostics and dataset validation. |


## Data Sources

The pipeline retrieves data from two CBS OData tables, four Eurostat indicators, and one CSV file hosted on GitHub containing Dutch Conjunctuurklol records.

### Immigration Data - CBS

| **Datatset** | **Purpose** |
| --- | --- |
| `85484NED` | Immigration observations using the country-of-origin dimension. |
| `83518NED` | Immigration observations using the migration-background dimension. |

The observations are standardized into three columns: `Period`, `Country`, and `Immigration` where immigration represents the count of persons.

### Economic Indicators - Eurostat

| **Indicator** | **Definition** | **Frequency** |
| --- | --- | --- |
| `MINWAGE` | National **Minimum Wages** expressed in purchasing-power standards. | Semiannual |
| `WAGESAL` | Seasonally and calendar-adjusted **Labour Cost Index** for wages and salaries. | Quarterly |
| `UNEMP` | **Unemployment Rate** as a percentage of the active population. | Monthly |
| `GDP` | Real **GDP Percentage Change** relative to the preceding period. | Quarterly |


### Business-Cycle Indicator -- Conjunctuurklok

The Dutch **Conjunctuurklok** is a statistic published by CBS that is designed to track short term movements in the Dutch business cycle. The monthly historical publications of this indicator form a series, which the pipeline attaches to the panel dataset by every matching country-month observation.

The inclusion of this indicator in the output dataset is configurable in `settings.py`.

## Feature Engineering

When FEATURE_ENGINEERING is enables, `features.py` creates additional economic features from the assembled economic indicators. The features capture changes within individual indicators and relative economic differences between origin countries and the Netherlands.

changes within individual countries and relative economic differences between origin countries and the Netherlands.

| **Feature** | **Calculation** |
| --- | --- |
| `UNEMP-GAP` | Origin unemployment rate − Dutch unemployment rate |
| `UNEMP-CHANGE` | Change in origin unemployment rate over 12 observations |
| `NL-UNEMP-CHANGE` | Change in Dutch unemployment rate over 12 observations |
| `WAGESAL-GROWTH` | Percentage growth in origin wages and salaries index over 12 observations |
| `NL-WAGESAL-GROWTH` | Percentage growth in Dutch wages and salaries index over 12 observations |
| `WAGESAL-GAP` | Dutch wages and salaries growth − origin wages and salaries growth |
| `MINWAGE-RATIO` | Dutch minimum wage ÷ origin minimum wage |
| `GDP-GROWTH-GAP` | Dutch real GDP growth − origin real GDP growth |

These transformations are calculated within each country after sorting observations chronologically. They assume a continuous monthly panel; observations without sufficient preceding history produce missing values.

Feature engineering takes place before the final period restriction, allowing available historical observations outside the output window to contribute to the calculated features.

## Output

The completed dataset is exported to:

**data\panel_data.csv**

Each row of the results CSV contains one row per country and month. `Period`,
`Country`, and `Immigration` retain their capitalized names. Country metrics
use a `Country-` prefix, and Netherlands benchmarks use an `NL-` prefix.

| Columns | Description |
| --- | --- |
| `Period` | Monthly period in YYYYMM format |
| `Country` | Origin country |
| `Immigration` | Monthly immigration observations |
| `Country-{CODE}` | Origin-country economic indicator |
| ` NL-{CODE}` | Corresponding Dutch economic benchmark |
| `NL-CONJCLK` | Dutch business-cycle indicator, when enabled |
| Engineered Features | Derived indicators described in the *Feature Engineering* section |

The dataset retains missing economic observations rather than automatically imputing them. Missing values may result from unavailable source observations or insufficient historical data for feature calculations.

Publication delays and forecasting-time information availability are handled separately in the downstream forecasting project.

The active period bounds are applied immediately before export, so changing
them limits the final CSV without modifying the downloaded source coverage.
