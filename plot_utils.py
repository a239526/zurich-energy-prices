from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_daily_prices(df, tariff_type, date, currency="USD", output_dir="outputs/plots"):
    # selects data for the specified day
    df_day = df[df['timestamp'].dt.strftime('%Y-%m-%d') == date].copy()

    if df_day.empty:
        print(f"No data available for {tariff_type} on {date}.")
        return

    df_day = df_day.sort_values('timestamp')

    # creates the output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # creates the plot
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        df_day['timestamp'],
        df_day['price_per_kwh'],
        label='Purchase price',
        linewidth=2
    )

    ax.plot(
        df_day['timestamp'],
        df_day['sell_price_per_kwh'],
        label='Selling price',
        linewidth=2
    )

    ax.set_title(f"{tariff_type.replace('_', ' ').title()} Electricity Prices - {date}")
    ax.set_xlabel("Time")
    ax.set_ylabel(f"Price ({currency}/kWh)")

    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()

    # saves the figure
    output_file = output_dir / f"{tariff_type}_prices_{date}.png"

    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"Plot saved to: {output_file}")