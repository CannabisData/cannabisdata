"""
Curate CCRS Strain Data
Copyright (c) 2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/25/2023
Updated: 2/6/2023
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Sources:

    - Washington State Liquor and Cannabis Board (WSLCB)
    URL: <https://lcb.box.com/s/wzfoqysl4v9aqljwc0pi0g5ea6bch759>

    - Curated CCRS Strain Statistics
    URL: <https://cannlytics.page.link/ccrs-strain-stats-2022-12-07>

"""
# Standard imports:
from datetime import datetime
import os

# External imports:
from cannlytics.utils import sorted_nicely
import pandas as pd


# Define the fields that will be used.
FIELDS = {
    'StrainType': 'string',
    'InventoryType': 'string',
    'UnitWeightGrams': 'string',
    'InitialQuantity': 'string',
    'QuantityOnHand': 'string',
    'strain_name': 'string',
}
NUMERIC = ['UnitWeightGrams', 'InitialQuantity', 'QuantityOnHand']


def curate_ccrs_strains(data_dir, stats_dir):
    """Curate CCRS strains by merging additional datasets."""

    print('Curating strains...')
    start = datetime.now()

    # Create stats directory if it doesn't already exist.
    inventory_dir = os.path.join(stats_dir, 'inventory')
    inventory_files = sorted_nicely(os.listdir(inventory_dir))

    # Calculate strain statistics using curated inventory items.
    strain_stats = pd.DataFrame({})
    for i, datafile in enumerate(inventory_files):
        print('Augmenting:', datafile, i + 1, '/', len(inventory_files))

        # Read the inventory items.
        data = pd.read_excel(
            os.path.join(inventory_dir, datafile),
            usecols=list(FIELDS.keys()),
            dtype=FIELDS,
        )

        # Get all inventory types of `InventoryType == 'Usable Marijuana'`
        flower = data.loc[data['InventoryType'] == 'Usable Marijuana']

        # Convert columns to numeric.
        for col in NUMERIC:
            flower[col] = flower[col].apply(
                lambda x: pd.to_numeric(x, errors='coerce')
            )

        # Sum `UnitWeightGrams` x `InitialQuantity` to get `total_weight`.
        total_weight = flower['UnitWeightGrams'].mul(flower['InitialQuantity'])

        # Sum `UnitWeightGrams` x (`InitialQuantity` - `QuantityOnHand`)
        # to get `total_sold`
        quantity_sold = flower['InitialQuantity'] - flower['QuantityOnHand']
        total_sold = flower['UnitWeightGrams'].mul(quantity_sold)

        # Convert weight to pounds.
        flower = flower.assign(
            total_weight = total_weight * 0.00220462,
            total_sold = total_sold * 0.00220462,
        )

        # Aggregate weights by `strain_name`.
        flower_stats = flower.groupby('strain_name').agg({
            'total_weight': 'sum',
            'total_sold': 'sum',
        })

        # Simply copy statistics on the first iteration.
        if i == 0:
            strain_stats = strain_stats.add(flower_stats, fill_value=0)

        # Otherwise, aggregate statistics.
        else:
            strain_weight = pd.concat(
                [strain_stats['total_weight'], flower_stats['total_weight']],
                axis=1
            ).sum(axis=1)
            strain_sold = pd.concat(
                [strain_stats['total_sold'], flower_stats['total_sold']],
                axis=1
            ).sum(axis=1)

            # Increment strain weight statistics.
            strain_stats = strain_stats.reindex(strain_weight.index)
            strain_stats.loc[strain_weight.index, 'total_weight'] = strain_weight

            # Increment strain sold statistics.
            strain_stats = strain_stats.reindex(strain_sold.index)
            strain_stats.loc[strain_sold.index, 'total_sold'] = strain_sold

        # Add strain type.
        flower_types = flower.groupby('strain_name')['StrainType'].first()
        strain_stats.loc[flower_types.index, 'strain_type'] = flower_types

    # Save the strain statistics.
    strains_dir = os.path.join(stats_dir, 'strains')
    if not os.path.exists(strains_dir): os.makedirs(strains_dir)
    outfile = os.path.join(strains_dir, 'strain-statistics.xlsx')
    strain_stats.to_excel(outfile)

    # Complete strains curation.
    end = datetime.now()
    print('✓ Finished curating strains in', end - start)
    return strain_stats


# === Test ===
if __name__ == '__main__':

    # Specify where your data lives.
    base = 'D:\\data\\washington\\'
    DATA_DIR = f'{base}\\CCRS PRR (1-27-23)\\CCRS PRR (1-27-23)\\'
    STATS_DIR = f'{base}\\ccrs-stats\\'
    curate_ccrs_strains(DATA_DIR, STATS_DIR)
