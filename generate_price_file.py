from tariff_utils import generate_price_file
from plot_utils import plot_daily_prices

# General configuration
OUTPUT_DIR = "outputs/prices"
CONVERT_TO_ZURICH = False
CONVERT_TO_USD = True
EXPORT_PRICE_RATIO = 0.2

TARIFF_TYPES = ["standard", "dynamic", "time_of_use"]

# Plot configuration
GENERATE_PLOTS = True
PLOT_DIR = "outputs/plots"
PLOT_DATES = ["2023-11-03"]

for tariff_type in TARIFF_TYPES:

    df = generate_price_file(
        tariff_type=tariff_type,
        convert_to_zurich=CONVERT_TO_ZURICH,
        convert_to_usd=CONVERT_TO_USD,
        export_price_ratio=EXPORT_PRICE_RATIO,
        output_dir=OUTPUT_DIR
    )

    # generates daily plots
    if GENERATE_PLOTS:
        for date in PLOT_DATES:
            plot_daily_prices(
                df=df,
                tariff_type=tariff_type,
                date=date,
            currency="USD" if CONVERT_TO_USD else "CHF",
            output_dir=PLOT_DIR
        )