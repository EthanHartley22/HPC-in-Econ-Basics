import os
import gc
from pathlib import Path
import polars as pl

# Constants
BASE_PATH = Path('/home/ehartley/koa_scratch/CMIP6/')
INPUT_PATH = BASE_PATH / 'Annual_Data_County/'
OUTPUT_PATH = BASE_PATH / 'Final_Monthly_Data/'
POPULATION_FILE = Path('/home/PRISM/prismGridPopulation.csv')

MODEL_LIST = [
    'ACCESS-CM2', 'ACCESS-ESM1-5', 'CanESM5', 'CMCC-ESM2', 'CNRM-CM6-1', 'CNRM-ESM2-1',
    'EC-Earth3', 'EC-Earth3-Veg-LR', 'FGOALS-g3', 'GFDL-ESM4', 'GISS-E2-1-G', 'INM-CM4-8',
    'INM-CM5-0', 'KACE-1-0-G', 'MIROC-ES2L', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0',
    'NorESM2-LM', 'NorESM2-MM', 'TaiESM1', 'UKESM1-0-LL'
]
SCENARIOS = ['ssp126', 'ssp245', 'ssp370', 'ssp585']

# Helper functions
def load_population_data():
    """Load and preprocess population data."""
    county_pops = pl.scan_csv(POPULATION_FILE)
    county_pops = county_pops.groupby('fips').agg(pl.col('pop').sum().alias('sum_pop'))
    county_pops = county_pops.with_columns(fips=pl.col('fips').cast(str).str.zfill(5))
    return county_pops

def process_files(model, scenario):
    """Process the model's scenario data and save it."""
    dataset_name = f'{model}_{scenario}_mean_monthly_weather.parquet'
    if (OUTPUT_PATH / dataset_name).exists():
        logger.info(f"Skipping {model}: Dataset already built")
        return

    logger.info(f"Processing {model} for scenario {scenario}")
    file_paths = list(INPUT_PATH.glob(f'*{scenario}*{model}*'))
    all_dfs = []

    for file_path in file_paths:
        df = pl.scan_parquet(file_path)
        all_dfs.append(df)

    df = pl.concat(all_dfs)
    df = df.with_columns(fips=pl.col('fips').cast(str).str.zfill(5))
    df = df.with_columns(stfips=pl.col('fips').str.slice(0, 2))

    # Extract year and month into new columns
    df = df.with_columns(year=pl.col('Date').dt.year(), month=pl.col('Date').dt.month())

    # Join with population data
    county_pops = load_population_data()
    df = df.join(county_pops, how='left', on='fips')

    # Calculate weighted averages
    columns = ['tMin', 'tMax', 'Avg_Temp'] + [f'CDD_{temp}' for temp in range(14, 23)] + [f'HDD_{temp}' for temp in range(14, 23)]
    weighted_averages = (pl.col(columns) * pl.col("sum_pop")).sum() / pl.col("sum_pop").sum()

    # Group by state, year, and month, and save the output
    df_state_month = df.groupby(["stfips", "year", "month"]).agg(weighted_averages).collect()
    df_state_month.write_parquet(OUTPUT_PATH / dataset_name)

    # Clear memory
    del df, county_pops, df_state_month
    gc.collect()

# Main function to iterate through all scenarios and models
def main():
    for scenario in SCENARIOS:
        logger.info(f"Processing scenario: {scenario}")
        for model in MODEL_LIST:
            process_files(model, scenario)

if __name__ == "__main__":
    main()