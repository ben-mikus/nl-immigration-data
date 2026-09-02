import pandas as pd


class ImmigrationPanel:
    """Assemble immigration observations and related monthly metrics."""

    def __init__(self, sources):
        if not sources:
            raise ValueError("At least one standardized panel source is required")

        combined = pd.concat(sources, ignore_index=True)
        required_columns = {"Period", "Country", "Immigration"}
        missing_columns = required_columns.difference(combined.columns)
        if missing_columns:
            raise ValueError(
                f"Standardized sources are missing required columns: {sorted(missing_columns)}"
            )

        self.data = combined.drop_duplicates(["Period", "Country"], keep="first")
        self.data = self.data.sort_values(["Country", "Period"], ignore_index=True)

    def absorb_country_metric(
        self,
        metric_data,
        metric_name,
        benchmark_country,
        benchmark_label="NL",
    ):
        """Add country, benchmark, and country-minus-benchmark metric fields."""
        required_columns = {"Period", "Country", metric_name}
        missing_columns = required_columns.difference(metric_data.columns)
        if missing_columns:
            raise ValueError(
                f"Metric data is missing required columns: {sorted(missing_columns)}"
            )
        if metric_data.duplicated(["Period", "Country"]).any():
            raise ValueError("Metric data contains duplicate Period/Country combinations")

        benchmark_column = f"{benchmark_label}-{metric_name}"
        country_column = f"Country-{metric_name}"
        difference_column = f"Diff-{metric_name}"

        benchmark_metric = metric_data.loc[
            metric_data["Country"].eq(benchmark_country),
            ["Period", metric_name],
        ].rename(columns={metric_name: benchmark_column})
        country_metric = metric_data.loc[
            ~metric_data["Country"].eq(benchmark_country),
            ["Period", "Country", metric_name],
        ].rename(columns={metric_name: country_column})

        self.data = self.data.merge(
            country_metric,
            on=["Period", "Country"],
            how="left",
        )
        self.data = self.data.merge(benchmark_metric, on="Period", how="left")
        self.data[difference_column] = (
            self.data[country_column] - self.data[benchmark_column]
        )

    def absorb_national_metric(self, metric_data, metric_name, country_label="NL"):
        """Add a national monthly metric to every matching country-panel row."""
        required_columns = {"Period", metric_name}
        missing_columns = required_columns.difference(metric_data.columns)
        if missing_columns:
            raise ValueError(
                f"Metric data is missing required columns: {sorted(missing_columns)}"
            )
        if metric_data.duplicated(["Period"]).any():
            raise ValueError("National metric data contains duplicate periods")

        self.data = self.data.merge(
            metric_data.rename(columns={metric_name: f"{country_label}-{metric_name}"}),
            on="Period",
            how="left",
        )

    def to_csv(self, output_file):
        """Write the assembled panel without its DataFrame index."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self.data.to_csv(output_file, index=False)
