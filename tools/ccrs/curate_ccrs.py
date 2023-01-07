"""
Curate CCRS Data
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/7/2023
Updated: 1/7/2023
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - Washington State Liquor and Cannabis Board (WSLCB)
    URL: <https://lcb.box.com/s/xseghpsq2t4i1musxj6mgd7b8rhxe7bm>

Command-line Usage:

    python tools/ccrs/curate_ccrs.py

"""
# Internal imports:
from .curate_ccrs_lab_results import curate_ccrs_lab_results
from .curate_ccrs_inventory import curate_ccrs_inventory
from .curate_ccrs_sales import curate_ccrs_sales


# === Test ===
if __name__ == '__main__':

    # Specify where your data lives.
    base = 'D:\\data\\washington\\'
    DATA_DIR = f'{base}\\CCRS PRR (12-7-22)\\CCRS PRR (12-7-22)\\'
    STATS_DIR = f'{base}\\ccrs-stats\\'
    curate_ccrs_lab_results(DATA_DIR, STATS_DIR)
    curate_ccrs_inventory(DATA_DIR, STATS_DIR)
    curate_ccrs_sales(DATA_DIR, STATS_DIR)
