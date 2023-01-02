"""
Curate CCRS Inventory
Copyright (c) 2022 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 1/1/2023
Updated: 1/1/2023
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - Washington State Liquor and Cannabis Board (WSLCB)
    URL: <https://lcb.box.com/s/xseghpsq2t4i1musxj6mgd7b8rhxe7bm>

"""
# Standard imports:
import os

# External imports:
from cannlytics.data.ccrs import (
    anonymize,
    get_datafiles,
    merge_datasets,
    unzip_datafiles,
)
from cannlytics.data.ccrs.constants import CCRS_DATASETS
from cannlytics.utils import rmerge
import pandas as pd


# Specify where your data lives.
DATA_DIR = 'D:\\data\\washington\\ccrs-2022-11-22\\ccrs-2022-11-22\\'
STATS_DIR = 'D:\\data\\washington\\ccrs-stats\\'


def curate_ccrs_inventory():
    """Curate CCRS inventory by merging additional datasets."""
    raise NotImplementedError


# === Test ===
if __name__ == '__main__':
    # curate_ccrs_inventory()

    # Unzip all CCRS datafiles.
    unzip_datafiles(DATA_DIR)

    # Read licensees data.
    licensees = pd.read_csv(
        f'{DATA_DIR}/Licensee_0/Licensee_0/Licensee_0.csv',
        sep='\t',
        encoding='utf-16',
        usecols=['LicenseeId', 'Name', 'DBA'],
        dtype={
            'LicenseeId': 'string',
            'Name': 'string',
            'DBA': 'string',
        },
    )
    columns = {'Name': 'retailer', 'DBA': 'retailer_dba'}
    licensees.rename(columns, axis=1, inplace=True)

    # Define all fields.
    # Note: `IsDeleted` throws a ValueError if it's a bool.
    fields = CCRS_DATASETS['inventory']['fields']
    date_fields = CCRS_DATASETS['inventory']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}

    # Create stats directory if it doesn't already exist.
    inventory_dir = os.path.join(STATS_DIR, 'inventory')
    if not os.path.exists(inventory_dir): os.makedirs(inventory_dir)

    # Iterate over all inventory datafiles to curate.
    inventory_files = get_datafiles(DATA_DIR, 'Inventory_')
    product_files = get_datafiles(DATA_DIR, 'Product_')
    lab_result_files = get_datafiles(DATA_DIR, 'LabResult_')
    for i, datafile in enumerate(inventory_files):
        print('Augmenting:', datafile)
        
        # DEV:
        # if i == 0:
        #     continue

        # Read in the items.
        items = pd.read_csv(
            datafile,
            sep='\t',
            encoding='utf-16',
            parse_dates=date_fields,
            usecols=item_cols,
            dtype=item_types,
        )

        # Merge items with licensee data.
        print('Merging licensee data...')
        items = rmerge(
            items,
            licensees,
            on='LicenseeId',
            how='left',
            validate='m:1',
        )
        print('Merged licensee data.')

        # Merge items with product data.
        print('Merging product data...')
        items = merge_datasets(
            items,
            product_files,
            dataset='products',
            on='ProductId',
            target='InventoryType',
            how='left',
            validate='m:1',
            rename={
               'CreatedDate': 'product_created_at',
               'updatedDate': 'product_updated_at',
               'ExternalIdentifier': 'product_external_id',
               'LicenseeId': 'producer_licensee_id',
            },
        )
        print('Merged product data.')

        # FIXME: Get lab results with `InventoryId`.
        # print('Merging lab result data...')
        # items = merge_datasets(
        #     items,
        #     lab_result_files,
        #     dataset='lab_results',
        #     on='InventoryId',
        #     target='total_thc',
        #     how='left',
        #     validate='m:1',
        #     rename={
        #        'CreatedDate': 'lab_result_created_at',
        #        'UpdatedDate': 'lab_result_updated_at',
        #        'ExternalIdentifier': 'lab_result_external_id',
        #        'LicenseeId': 'producer_licensee_id',
        #     },
        # )
        # print('Merged lab result data.')

        # Save the curated inventory data.
        print('Saving the curated inventory data...')
        outfile = os.path.join(inventory_dir, f'Inventory_{i}.xlsx')
        items = anonymize(items)
        items.to_excel(outfile, index=False)
        print('Curated inventory datafile:', i, '/', len(inventory_files))
