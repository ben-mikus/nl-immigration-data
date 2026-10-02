# Netherlands Immigration Panel

Build a monthly panel of Dutch immigration observations and economic indicators
for a selected origin country. The current configuration compares Poland with
the Netherlands using minimum wages in purchasing-power standards, the
wages-and-salaries Labour Cost Index, and the Dutch Conjunctuurklok.

## Setup and run

Use Python 3.12 or later, then install the two runtime dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install pandas requests
.\.venv\Scripts\python main.py
```

The pipeline retrieves CBS and Eurostat data at runtime and writes the final
panel to `data\panel_data.csv`. It does not persist raw API responses.

## Configure the panel

Edit `config.py` to adapt the panel. The principal configuration surfaces are:

| Goal | Configuration |
| --- | --- |
| Change the output period | Set `PANEL_START_PERIOD` and `PANEL_END_PERIOD` to inclusive `YYYYMM` values, such as `"201001"` and `"202512"`. |
| Change the origin country | Update the CBS country dimension code in both `CBS_TABLES` filters, `CBS_COUNTRY_NAME_REPLACEMENTS`, `EUROSTAT_COUNTRY_NAME_REPLACEMENTS`, and the `geo` entries in every metric. Keep `NL` and `"Netherlands"` when a Dutch benchmark is required. |
| Change economic indicators | Replace or add entries in `EUROSTAT_METRICS`. Each entry needs a Eurostat dataset ID, a metric name, benchmark settings, frequency, and the dataset's API dimension filters. |
| Use monthly, quarterly, or half-yearly Eurostat data | Omit `frequency` or use `"M"` for monthly data; use `"Q"` for quarterly data and `"S"` for half-yearly data. Quarterly and half-yearly values are repeated across the months they cover. |
| Configure minimum wages | The current `earn_mw_cur` entry requests half-yearly national minimum wages in PPS using `("currency", "PPS")`. Change the currency filter to `EUR` or `NAC` when needed. |
| Configure the Labour Cost Index | The current `lc_lci_r2_q` entry requests `D11` wages and salaries, seasonally and calendar adjusted (`SCA`), as a 2020=100 index (`I20`) for the `B-S` economy. Change these filters to select another component, adjustment, unit, or industry scope. |
| Replace the Dutch business-cycle series | Update `table-conjunctuur-indicator.csv`. It must provide `Periode` and `Cyclus` columns; supported period formats are Dutch month names such as `januari 2025` and abbreviations such as `Jan-25`. |
| Remove the local business-cycle series | Remove the `panel.absorb_national_metric(...)` call in `main.py` and the associated `load_conjunctuurklok` import. |

`ImmigrationPanel` combines metrics by `Period` and `Country`. It writes the
country value and the Dutch benchmark value as separate columns; it does not
calculate difference columns.

## Output

`data\panel_data.csv` contains one row per country and month. `Period`,
`Country`, and `Immigration` retain their capitalized names. Country metrics
use a `Country-` prefix, and Netherlands benchmarks use an `NL-` prefix.

| Code | Meaning |
| --- | --- |
| `MINWAGE` | National minimum wage in purchasing-power standards (PPS). |
| `WAGESAL` | Wages-and-salaries Labour Cost Index; seasonally and calendar adjusted, 2020=100, whole economy. |
| `CONJCLK` | Dutch Conjunctuurklok business-cycle indicator. |

The active period bounds are applied immediately before export, so changing
them limits the final CSV without modifying the downloaded source coverage.
