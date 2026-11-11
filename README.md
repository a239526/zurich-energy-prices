# Swiss Electricity Prices

## Overview

This repository provides Python scripts to generate electricity price CSV files and daily price plots for Switzerland using the dataset published by Kaiser et al. (2026).

The dataset contains electricity tariff data at **15-minute intervals**, allowing the generation of time-series electricity prices for different tariff structures. It covers the period from **January 1, 2023, to December 31, 2024**, providing two years of electricity tariff data.

The generated CSV files contain the following columns:

| Column | Description |
|---|---|
| `timestamp` | Timestamp of the price measurement |
| `price_per_kwh` | Electricity purchase price (USD/kWh or CHF/kWh) |
| `sell_price_per_kwh` | Electricity export price (USD/kWh or CHF/kWh) |

The repository currently supports three tariff types:
- **Standard:** Standard electricity tariff.
- **Dynamic:** Dynamic electricity tariff.
- **Time-of-use (TOU):** Time-dependent electricity tariff.

Additionally, the scripts can generate daily plots comparing electricity purchase and export prices for selected dates.

## Data Source

The electricity tariff data used in this repository comes from:

Kaiser, K., Kreft, M., González Vayá, M., & Hug, H. (2026). *Dataset on residential electricity load profiles in Switzerland* (Version v1) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.21398769

All original tariff values are provided in Rp./kWh (Swiss Rappen per kilowatt-hour). The scripts convert these values to CHF/kWh and optionally to USD/kWh.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/a239526/zurich-energy-prices/
cd zurich-energy-prices
```

### 2. Create and activate a virtual environment

Create the virtual environment:

```bash
python -m venv .venv
```

Activate it:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate price CSV files and plots

Run the main script:

```bash
python generate_price_file.py
```

The generated CSV files will be saved in the `outputs/prices/` directory. If plot generation is enabled, the daily plots will be saved in the `outputs/plots/` directory.

## Configuration

The generation process can be configured directly in `generate_price_file.py`.

### General configuration

```python
OUTPUT_DIR = "prices"
CONVERT_TO_ZURICH = False
CONVERT_TO_USD = True
EXPORT_PRICE_RATIO = 0.2

TARIFF_TYPES = ["standard", "dynamic", "time_of_use"]
```

The parameters can be adjusted as follows:

| Parameter | Description |
|---|---|
| `OUTPUT_DIR` | Directory where the generated CSV files are saved. |
| `CONVERT_TO_ZURICH` | If `True`, converts timestamps from UTC to the `Europe/Zurich` timezone. Otherwise, timestamps remain in UTC. |
| `CONVERT_TO_USD` | If `True`, converts prices from CHF to USD. Otherwise, prices remain in CHF. |
| `EXPORT_PRICE_RATIO` | Defines the ratio between the electricity export price and the purchase price. For example, `0.2` means that the export price is 20% of the purchase price. |
| `TARIFF_TYPES` | List of tariff types to generate. Supported values are `standard`, `dynamic`, and `time_of_use`. |

### Plot configuration

Plot generation is optional and can be enabled or disabled independently of CSV generation.

```python
GENERATE_PLOTS = True
PLOT_DIR = "plots"
PLOT_DATES = ["2023-10-15"]
```

| Parameter | Description |
|---|---|
| `GENERATE_PLOTS` | If `True`, generates daily price plots. If `False`, only the CSV files are generated. |
| `PLOT_DIR` | Directory where the generated plots are saved. |
| `PLOT_DATES` | List of dates for which daily plots should be generated, using the `YYYY-MM-DD` format. |

For each selected date, the script generates a plot for every tariff type in `TARIFF_TYPES`. Each plot displays the electricity purchase and export prices over the selected day.

For example, to generate plots for October 15 and October 16, 2023:

```python
PLOT_DATES = ["2023-10-15", "2023-10-16"]
```

To skip plot generation while still generating all CSV files:

```python
GENERATE_PLOTS = False
```

### Tariff Types

The repository supports three electricity tariff structures:

#### Standard Tariff

Uses the standard electricity tariff, combining energy and grid charges. The dataset provides complete data for the entire period covered by the repository (January 1, 2023, to December 31, 2024).


#### Dynamic Tariff

Uses time-varying electricity prices, combining energy and grid charges. Although the original dataset only provides complete dynamic tariff data starting in October 2023, missing values are reconstructed using synthetic daily profiles generated from available real tariff data with perturbations.

The reconstruction is performed as follows:
- Complete daily tariff profiles are selected as reference days, requiring all 96 15-minute intervals to have valid energy and grid tariff values.
- Missing daily profiles in 2022 and 2023 are reconstructed using reference days from 2023, while missing profiles in 2024 use reference days from 2024.
- For each missing day, a reference day with the same weekday is randomly selected, preserving the weekly tariff pattern.
- Synthetic profiles are generated from the selected real profiles: missing energy tariff values (`energy_unit_cn`) are copied directly, while missing grid tariff values (`grid_dyn`) are reconstructed by applying independent random perturbations uniformly distributed between -10% and +10% to each 15-minute interval.
- Existing tariff values are preserved, and only missing values (`NaN`) are replaced.
- A fixed random seed is used to ensure reproducibility of the synthetic profiles.

This approach allows the dynamic tariff data to be extended to the entire period (January 1, 2023, to December 31, 2024), providing complete daily profiles while preserving the weekly structure of electricity prices and introducing small variations in the reconstructed grid tariff values.

#### Time-of-use (TOU) Tariff

Uses electricity prices that vary according to the time of day, combining energy and grid charges. Although the original dataset only provides TOU values starting in October 2023, the missing values are reconstructed based on the recurring daily tariff profiles.

For 2023, the TOU tariff follows the same 15-minute price profile every day, with two distinct profiles depending on whether daylight saving time (DST) is in effect. The reconstruction is performed as follows:
- Timestamps are converted to the `Europe/Zurich` timezone to correctly identify daylight saving time and standard time.
- Two separate tariff profiles are considered: one for daylight saving time (CEST) and another for standard time (CET).
- Within each profile, tariff values are grouped by their local 15-minute interval.
- Missing energy and grid tariff values (`NaN`) are replaced with the first available value for the corresponding 15-minute interval and seasonal profile, while existing values are preserved.

This approach allows the TOU tariff data to be extended to the entire period (January 1, 2023, to December 31, 2024).

## Output

### CSV files

The generated files are saved in the directory specified by `OUTPUT_DIR` (default: `prices/`).

Each tariff type generates a separate CSV file:

```text
prices/
├── standard_prices.csv
├── dynamic_prices.csv
└── time_of_use_prices.csv
```

Each CSV follows the same structure:

```csv
timestamp,price_per_kwh,sell_price_per_kwh
2022-12-31 23:00:00+00:00,0.272000,0.054400
2022-12-31 23:15:00+00:00,0.272000,0.054400
2022-12-31 23:30:00+00:00,0.272000,0.054400
2022-12-31 23:45:00+00:00,0.272000,0.054400
```

All numerical values are saved with six decimal places.

### Daily plots

When `GENERATE_PLOTS = True`, the script saves one PNG plot for each combination of tariff type and selected date.

For example, with the default configuration:

```text
plots/
├── standard_prices_2023-10-15.png
├── dynamic_prices_2023-10-15.png
└── time_of_use_prices_2023-10-15.png
```

Each plot shows the purchase and export prices throughout the selected day. The vertical axis indicates the price in USD/kWh or CHF/kWh, depending on the `CONVERT_TO_USD` setting.

Both output directories are created automatically if they do not already exist.

## Repository Structure

```text
zurich-energy-prices/
│
├── outputs/                # Generated CSV files and daily price plots
│
├── tariff_data.csv          # Original tariff dataset
├── tariff_utils.py          # Functions for loading and processing tariff data
├── plot_utils.py            # Functions for generating daily price plots
├── generate_price_file.py   # Main script for generating CSV files and plots
│
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

## Notes

- The original dataset uses Swiss Rappen (Rp.) per kWh. Prices are divided by 100 to obtain CHF/kWh.
- Currency conversion from CHF to USD depends on the exchange rate configured in `tariff_utils.py`.
- Timestamps are originally provided in UTC. Timezone conversion to `Europe/Zurich` is optional.
- The export price is calculated as a fixed proportion of the purchase price, according to `EXPORT_PRICE_RATIO`.
- Missing tariff values are handled according to the tariff structure: TOU values are reconstructed using the corresponding hourly tariff profiles, while synthetic dynamic tariff values are generated from available real tariff data with perturbations. 
- Plot generation is optional and does not affect CSV generation.

## Citation

If you use the dataset or the generated price series in your research, please cite the original dataset:

Kaiser, K., Kreft, M., González Vayá, M., & Hug, H. (2026). *Dataset on residential electricity load profiles in Switzerland* (Version v1) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.21398769
