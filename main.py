
import pandas as pd

from cbs import (
    combine_panel_sources,
    get_odata,
    layer_country_metric,
    layer_national_metric,
    standardize_conjunctuurklok,
    standardize_immigration_observations,
)
from eurostat import (
    country_name_replacements as eurostat_country_name_replacements,
    eurostat_metrics,
    get_eurostat,
    standardize_eurostat_observations,
)


data_directory = "data"
country_name_replacements = {
    "Bulgarije": "Bulgaria",
    "Polen": "Poland",
    "Roemenië": "Romania",
}

tables = [
    {
        "id": "85484NED",
        "country_column": "Herkomstland",
        "country_codes_endpoint": "HerkomstlandCodes",
        "country_codes_file_stem": "herkomstland_codes",
        "params": {
            "$filter": (
                "Measure eq 'M000167' "                     # Immigration
                "and substring(Perioden,4,2) eq 'MM' "      # Monthly observations
                "and Geboorteland eq 'T001638' "            # Total (country of birth)
                "and Geslacht eq 'T001038' "                # Total (men and women)
                "and ("
                "Herkomstland eq 'H008718' "                # Poland (country of origin)
                "or Herkomstland eq 'H008567' "             # Bulgaria (country of origin)
                "or Herkomstland eq 'H008723' "             # Romania (country of origin)
                ")"
            )
        },
    },
    {
        "id": "83518NED",
        "country_column": "Migratieachtergrond",
        "country_codes_endpoint": "MigratieachtergrondCodes",
        "country_codes_file_stem": "migratieachtergrond_codes",
        "params": {
            "$filter": (
                "Measure eq 'M000167' "                     # Immigration
                "and substring(Perioden,4,2) eq 'MM' "      # Monthly observations
                "and Generatie eq 'T001040' "               # Total (generation)
                "and Geslacht eq 'T001038' "                # Total (men and women)
                "and ("
                "Migratieachtergrond eq 'H008718' "         # Poland (migration background)
                "or Migratieachtergrond eq 'H008567' "      # Bulgaria (migration background)
                "or Migratieachtergrond eq 'H008723' "      # Romania (migration background)
                ")"
            )
        },
    },
]


def extract_and_standardize(table):
    table_url = f"https://datasets.cbs.nl/odata/v1/CBS/{table['id']}"
    observations = get_odata(f"{table_url}/Observations", table["params"])
    observations.to_csv(f"{data_directory}/{table['id']}.csv", index=False)

    country_codes = get_odata(
        f"{table_url}/{table['country_codes_endpoint']}"
    )
    country_codes.to_csv(
        f"{data_directory}/{table['id']}_{table['country_codes_file_stem']}.csv",
        index=False,
    )

    return standardize_immigration_observations(
        observations,
        country_codes,
        country_name_replacements,
        table["country_column"],
    )


standardized_sources = [extract_and_standardize(table) for table in tables]
combined_data = combine_panel_sources(*standardized_sources)


def extract_and_layer_eurostat_metric(panel, metric):
    observations = get_eurostat(metric["id"], metric["params"])
    observations.to_csv(f"{data_directory}/{metric['id']}.csv", index=False)

    standardized_metric = standardize_eurostat_observations(
        observations,
        metric["metric_name"],
        eurostat_country_name_replacements,
        metric.get("frequency", "M"),
    )
    return layer_country_metric(
        panel,
        standardized_metric,
        metric["metric_name"],
        metric["benchmark_country"],
        metric["benchmark_label"],
    )


panel_data = combined_data
for metric in eurostat_metrics:
    panel_data = extract_and_layer_eurostat_metric(panel_data, metric)

conjunctuurklok_data = pd.read_csv("table-conjunctuur-indicator.csv")
standardized_conjunctuurklok = standardize_conjunctuurklok(conjunctuurklok_data)
panel_data = layer_national_metric(
    panel_data,
    standardized_conjunctuurklok,
    "Conjunctuurklok",
)

panel_data.to_csv(f"{data_directory}/panel_data.csv", index=False)
