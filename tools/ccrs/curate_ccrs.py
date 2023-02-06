"""
Curate CCRS Data
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 1/7/2023
Updated: 2/6/2023
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - Washington State Liquor and Cannabis Board (WSLCB)
    URL: <https://lcb.box.com/s/wzfoqysl4v9aqljwc0pi0g5ea6bch759>

Command-line Usage:

    python tools/ccrs/curate_ccrs.py

"""
# Internal imports:
from .curate_ccrs_lab_results import curate_ccrs_lab_results
from .curate_ccrs_inventory import curate_ccrs_inventory
from .curate_ccrs_sales import curate_ccrs_sales
from .curate_ccrs_strains import curate_ccrs_strains


# === Test ===
if __name__ == '__main__':

    # Specify where your data lives.
    base = 'D:\\data\\washington\\'
    DATA_DIR = f'{base}\\CCRS PRR (1-27-23)\\CCRS PRR (1-27-23)\\'
    STATS_DIR = f'{base}\\ccrs-stats\\'
    curate_ccrs_lab_results(DATA_DIR, STATS_DIR)
    curate_ccrs_inventory(DATA_DIR, STATS_DIR)
    curate_ccrs_sales(DATA_DIR, STATS_DIR)
    curate_ccrs_strains(DATA_DIR, STATS_DIR)
