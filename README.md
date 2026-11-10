# Swiss Electricity Prices

## Overview

This repository provides Python scripts to generate electricity price CSV files for Switzerland using the dataset published by Kaiser et al. (2026).

The dataset contains electricity tariff data at **15-minute intervals**, allowing the generation of time-series electricity prices for different tariff structures.

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

## Data Source

The electricity tariff data used in this repository comes from:

Kaiser, K., Kreft, M., González Vayá, M., & Hug, G. (2026). *Dataset on residential electricity load profiles in Switzerland* (Version v1) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.21398769

All original tariff values are provided in Rp./kWh (Swiss Rappen per kilowatt-hour). The scripts convert these values to CHF/kWh and optionally to USD/kWh.

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
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

### 4. Generate the price CSV files

Run the main script:

```bash
python generate_price_file.py
```

The generated CSV files will be saved in the `prices/` directory.

## Configuration

The generation process can be configured directly in `generate_price_file.py`.

The following parameters are available:

```python
from tariff_utils import generate_price_file

OUTPUT_DIR = "prices"
CONVERT_TO_ZURICH = False
CONVERT_TO_USD = True
EXPORT_PRICE_RATIO = 0.2
TARIFF_TYPES = ["standard", "dynamic", "time_of_use"]

for tariff_type in TARIFF_TYPES:
    generate_price_file(
        tariff_type=tariff_type,
        convert_to_zurich=CONVERT_TO_ZURICH,
        convert_to_usd=CONVERT_TO_USD,
        export_price_ratio=EXPORT_PRICE_RATIO,
        output_dir=OUTPUT_DIR
    )
```

The parameters can be adjusted as follows:

| Parameter | Description |
|---|---|
| `OUTPUT_DIR` | Directory where the generated CSV files are saved. |
| `CONVERT_TO_ZURICH` | If `True`, converts timestamps from UTC to the `Europe/Zurich` timezone. Otherwise, timestamps remain in UTC. |
| `CONVERT_TO_USD` | If `True`, converts prices from CHF to USD. Otherwise, prices remain in CHF. |
| `EXPORT_PRICE_RATIO` | Defines the ratio between the electricity export price and the purchase price. For example, `0.2` means that the export price is 20% of the purchase price. |
| `TARIFF_TYPES` | List of tariff types to generate. Supported values are `standard`, `dynamic`, and `time_of_use`. |

### Tariff availability

The different tariff structures have different data availability periods (Europe/Zurich timezone):

| Tariff | Available period |
|---|---|
| Standard | January 1, 2023 – December 31, 2024 |
| Dynamic | October 1 2023 – December 31, 2024 |
| Time-of-use (TOU) | October 1 2023 – December 31, 2024 |

The dynamic and time-of-use tariffs are only available starting in October 2023. The generation scripts automatically filter out timestamps for which the corresponding tariff data is unavailable.

## Output

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

The output directory is created automatically if it does not already exist.

## Repository Structure

```text
zurich-energy-prices/
│
├── prices/                  # Generated electricity price CSV files
│
├── tariff_data.csv          # Original tariff dataset
├── tariff_utils.py          # Functions for loading and processing tariff data
├── generate_price_file.py   # Main script for generating price CSV files
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
- Missing tariff values are excluded from the corresponding generated time series.

## Citation

If you use the dataset or the generated price series in your research, please cite the original dataset:

Kaiser, K., Kreft, M., González Vayá, M., & Hug, G. (2026). *Dataset on residential electricity load profiles in Switzerland* (Version v1) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.21398769
