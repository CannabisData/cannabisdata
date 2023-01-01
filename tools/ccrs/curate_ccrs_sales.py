"""
Curate CCRS Sales
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

    # Create stats directory if it doesn't already exist.
    sales_dir = os.path.join(STATS_DIR, 'sales')
    if not os.path.exists(STATS_DIR): os.makedirs(STATS_DIR)

    # Iterate over all sales items files to calculate stats.
    daily_licensee_sales = {}
    sales_items_files = get_datafiles(DATA_DIR, 'SalesDetail_')
    for i, datafile in enumerate(sales_items_files):
        print('Augmenting:', datafile)

        # TODO: Read curated inventory.
