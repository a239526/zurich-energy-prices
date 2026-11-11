import os
import pandas as pd
import numpy as np

DATA_FILE = "tariff_data.csv"
CHF_TO_USD = 1.21 
OUTPUT_DIR = "outputs/prices"

def load_tariff_data():
    # loads the tariff data from the CSV file
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Tariff data file {DATA_FILE} not found.")
    df = pd.read_csv(DATA_FILE, sep=";")

    return df

def timezone_conversion(df, df_new, convert_to_zurich=True):
    timestamp = pd.to_datetime(df['timestamp_utc'], utc=True)

    # converts timestamp from UTC to Europe/Zurich timezone if requested
    if convert_to_zurich:
        timestamp = timestamp.dt.tz_convert('Europe/Zurich')

    df_new['timestamp'] = timestamp

    return df_new

def standard_tariff(df, df_new, convert_to_usd=True):
    # calculates the standard tariff (energy + grid) in CHF/kWh
    df_new['price_per_kwh'] = (df['energy_standard'] + df['grid_standard']) / 100

    # converts from CHF to USD if requested
    if convert_to_usd:
        df_new['price_per_kwh'] *= CHF_TO_USD

    return df_new



def dynamic_tariff(df, df_new, convert_to_usd=True, seed=42):
    rng = np.random.default_rng(seed)

    data = df[['timestamp_utc', 'energy_unit_cn', 'grid_dyn']].copy()
    ts = pd.to_datetime(data['timestamp_utc'], utc=True)

    # extracts date, year, weekday and 15-min slot from the timestamp
    data['_day'] = ts.dt.date
    data['_year'] = ts.dt.year
    data['_weekday'] = ts.dt.weekday
    data['_slot'] = ts.dt.hour * 4 + ts.dt.minute // 15

    # selects complete daily tariff profiles
    profiles = {}
    for year in [2023, 2024]:
        profiles[year] = {}
        for day, group in data[data['_year'] == year].groupby('_day'):
            # skips December 31st to avoid transition data
            if str(day) == '2023-12-31':
                continue
            if len(group) == 96 and group[['energy_unit_cn', 'grid_dyn']].notna().all().all():
                profiles[year].setdefault(group['_weekday'].iloc[0], []).append(
                    group.set_index('_slot')[['energy_unit_cn', 'grid_dyn']]
                )

    # fills missing tariff values using random days of the same weekday
    missing_days = data[data[['energy_unit_cn', 'grid_dyn']].isna().any(axis=1)]['_day'].unique()

    for day in missing_days:
        group = data[data['_day'] == day]
        year = group['_year'].iloc[0]
        weekday = group['_weekday'].iloc[0]
        # selects the source year for filling missing data
        source_year = 2023 if year in [2022, 2023] else 2024

        candidates = profiles[source_year].get(weekday, [])
        if not candidates:
            print(f'No complete tariff profiles available for filling missing data on {day}. Skipping.')
            continue

        profile = candidates[rng.integers(len(candidates))]
        idx = group.index
        slots = group['_slot']

        for col in ['energy_unit_cn', 'grid_dyn']:
            missing = data.loc[idx, col].isna()
            missing_idx = idx[missing]

            values = slots.loc[missing_idx].map(profile[col])

            if col == 'grid_dyn':
                values *= rng.uniform(0.9, 1.1, len(missing_idx))

            data.loc[missing_idx, col] = values.values

    # calculates the dynamic tariff (energy + grid) in CHF/kWh
    df_new['price_per_kwh'] = (
        data['energy_unit_cn'] + data['grid_dyn']
    ) / 100

    # converts from CHF to USD
    if convert_to_usd:
        df_new['price_per_kwh'] *= CHF_TO_USD

    return df_new

def time_of_use_tariff(df, df_new, convert_to_usd=True):
    # converts timestamps to Zurich timezone
    timestamp = pd.to_datetime(df['timestamp_utc'], utc=True).dt.tz_convert('Europe/Zurich')

    # extracts local hour, minute and daylight saving time status
    hour = timestamp.dt.hour
    minute = timestamp.dt.minute
    dst = timestamp.map(lambda t: t.dst() != pd.Timedelta(0))

    # fills missing TOU data using the corresponding seasonal 15-min profile
    energy = df['energy_unit_cn'].fillna(
        df['energy_unit_cn'].groupby([dst, hour, minute]).transform('first')
    )
    grid = df['grid_tou'].fillna(
        df['grid_tou'].groupby([dst, hour, minute]).transform('first')
    )

    # calculates the time-of-use tariff (energy + grid) in CHF/kWh
    df_new['price_per_kwh'] = (energy + grid) / 100

    # converts from CHF to USD if requested
    if convert_to_usd:
        df_new['price_per_kwh'] *= CHF_TO_USD

    return df_new

def sell_price(df_new, export_price_ratio=0.2):
    # calculates the selling price
    df_new['sell_price_per_kwh'] = df_new['price_per_kwh'] * export_price_ratio

    return df_new

def generate_price_file(tariff_type="standard", convert_to_zurich=True, convert_to_usd=True, export_price_ratio=0.2, output_dir=OUTPUT_DIR):

    # creates the output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # loads the original tariff data
    df = load_tariff_data()

    # creates a new DataFrame
    df_new = pd.DataFrame()

    # converts timestamps
    df_new = timezone_conversion(df, df_new, convert_to_zurich)

    # selects the tariff type
    if tariff_type == "standard":
        df_new = standard_tariff(df, df_new, convert_to_usd)

    elif tariff_type == "dynamic":
        df_new = dynamic_tariff(df, df_new, convert_to_usd)

    elif tariff_type == "time_of_use":
        df_new = time_of_use_tariff(df, df_new, convert_to_usd)

    # calculates selling price
    df_new = sell_price(df_new, export_price_ratio)

    # saves the resulting CSV
    output_file = os.path.join(OUTPUT_DIR, f"{tariff_type}_prices.csv")
    df_new.to_csv(output_file, index=False, float_format='%.6f')

    print(f"Price file saved to: {output_file}")

    return df_new