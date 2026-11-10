from tariff_utils import generate_price_file

CONVERT_TO_ZURICH = True
CONVERT_TO_USD = True
EXPORT_PRICE_RATIO = 0.2
TARIFF_TYPES = ["standard", "dynamic", "time_of_use"]

for tariff_type in TARIFF_TYPES:
    generate_price_file(
        tariff_type=tariff_type,
        convert_to_zurich=CONVERT_TO_ZURICH,
        convert_to_usd=CONVERT_TO_USD,
        export_price_ratio=EXPORT_PRICE_RATIO)