"""
CCRS Sales by Licensee
Copyright (c) 2022 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/23/2022
Updated: 12/25/2022
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - Washington State Liquor and Cannabis Board (WSLCB)
    URL: <https://lcb.box.com/s/xseghpsq2t4i1musxj6mgd7b8rhxe7bm>

"""
# Standard imports:
from datetime import datetime
import os
from zipfile import ZipFile

# External imports:
from cannlytics.data.ccrs.constants import CCRS_DATASETS
from cannlytics.utils import rmerge, sorted_nicely
import pandas as pd


def get_ccrs_datafiles(data_dir, dataset='', desc=True):
    """Get all CCRS datafiles of a given type in a directory."""
    files = os.listdir(data_dir)
    datafiles = [f'{data_dir}/{f}/{f}/{f}.csv' for f in files if f.startswith(dataset)]
    datafiles = sorted_nicely(datafiles)
    if desc:
        datafiles.reverse()
    return datafiles


def unzip_ccrs(data_dir, verbose=True):
    """Unzip all CCRS datafiles."""
    zip_files = [f for f in os.listdir(data_dir) if f.endswith('.zip')]
    for zip_file in zip_files:
        filename = os.path.join(data_dir, zip_file)
        zip_dest = filename.rstrip('.zip')
        if not os.path.exists(zip_dest):
            os.makedirs(zip_dest)
        zip_ref = ZipFile(filename)
        zip_ref.extractall(zip_dest)
        zip_ref.close()
        os.remove(filename)
        if verbose:
            print('Unzipped:', zip_file)


# === Test ===
if __name__ == '__main__':

    # Specify where your data lives.
    DATA_DIR = 'D:\\data\\washington\\ccrs-2022-11-22\\ccrs-2022-11-22\\'
    STATS_DIR = 'D:\\data\\washington\\ccrs-stats\\'

    # Unzip all CCRS datafiles.
    unzip_ccrs(DATA_DIR)

    # Define statistics to calculate.
    daily_licensee_sales = {}

    # Identify all of the sales datafiles.
    sales_items_files = get_ccrs_datafiles(DATA_DIR, 'SalesDetail')

    # Define all sales fields.
    fields = CCRS_DATASETS['sale_details']['fields']
    date_fields = CCRS_DATASETS['sale_details']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}

    # Hot-fix for ValueError: cannot safely convert passed user dtype of bool for object dtyped data in column 10
    item_types['IsDeleted'] = 'string'

    # Define all sales headers fields.
    supp_fields = CCRS_DATASETS['sale_headers']['fields']
    supp_date_fields = CCRS_DATASETS['sale_headers']['date_fields']
    supp_cols = list(supp_fields.keys()) + supp_date_fields
    supp_types = {k: supp_fields[k] for k in supp_fields if k not in supp_date_fields}

    # Iterate over all sales items files.
    for i, datafile in enumerate(sales_items_files):

        # Read in the sales items.
        items = pd.read_csv(
            datafile,
            sep='\t',
            encoding='utf-16',
            parse_dates=date_fields,
            usecols=item_cols,
            dtype=item_types,
        )

        # Remove any sales items that were deleted.
        items = items.loc[(items['IsDeleted'] != 'True') & (items['IsDeleted'] != True)]
        item_count = len(items)

        # Iterate over the sales headers until all items have been augmented.
        # Note: There is probably a clever way to reduce the number of times
        # that the headers are read. Currently reads all current to earliest then
        # reads earliest to current for the 2nd half to reduce unnecessary reads.
        augmented = pd.DataFrame()
        if i < len(sales_items_files) / 2:
            sale_headers_files = get_ccrs_datafiles(DATA_DIR, 'SaleHeader')
        else:
            sale_headers_files = get_ccrs_datafiles(DATA_DIR, 'SaleHeader', desc=False)
        for filename in sale_headers_files:

            # Read in the sale headers data to supplement the sales data.
            try:
                supplement = pd.read_csv(
                    filename,
                    sep='\t',
                    encoding='utf-16',
                    parse_dates=supp_date_fields,
                    usecols=supp_cols,
                    dtype=supp_types,
                )
            except OSError:
                continue

            # Merge sales details with sale headers.
            data = rmerge(items, supplement, on='SaleHeaderId', how='left')
            augmented = pd.concat([augmented, data.loc[~data['LicenseeId'].isna()]])

            # TODO: Merge with inventory data to get `ProductId`.


            # TODO: Merge with product data to get `InventoryType`, `Name`,
            # `Description`, `UnitWeightGrams`.


            # TODO: Get all lab results with `InventoryId`.
        

            # Stop iterating once all items have been matched.
            print(
                'Matched %.2f%%' % (len(augmented) / item_count * 100),
                f'of {datafile.split("/")[-1]}'
            )
            if len(augmented) == item_count:
                break

        # At this stage, sales by licensee by day can be incremented.
        # Note: The absolute value of the `Discount` is used.
        group = ['LicenseeId', 'SaleDate']
        daily_sales = augmented.groupby(group, as_index=False).sum()
        for index, row in daily_sales.iterrows():
            licensee_id = row['LicenseeId']
            date = row['SaleDate'].isoformat()[:10]
            licensee_sales = daily_licensee_sales.get(licensee_id, {})
            date_sales = licensee_sales.get(date, {})
            licensee_sales[date] = {
                'total_price': date_sales.get('total_price', 0) + row['UnitPrice'],
                'total_discount': date_sales.get('total_discount', 0) + abs(row['Discount']),
                'total_sales_tax': date_sales.get('total_sales_tax', 0) + row['SalesTax'],
                'total_other_tax': date_sales.get('total_other_tax', 0) + row['OtherTax'],
            }
            daily_licensee_sales[licensee_id] = licensee_sales


        # TODO: Save the augmented sales to licensee-specific files,
        # sharding as needed to keep files under 1 million observations.


    # Compile the statistics.
    stats = []
    for licensee_id, dates in daily_licensee_sales.items():
        for date, values in dates.items():
            stats.append({
                'licensee_id': licensee_id,
                'date': date,
                **values,
            })
    
    # TODO: Add licensee data.

    
    # Save the statistics.
    timestamp = datetime.now().isoformat()[:19].replace(':', '-')
    stats = pd.DataFrame(stats)
    stats.to_excel(f'{STATS_DIR}/sales-by-licensee.xlsx', index=False)


    #--------------------------------------------------------------------------
    # The 420 Awards
    #--------------------------------------------------------------------------

    # Who sold the most on 4/20/2022?
    april_20 = stats.loc[stats['date'] == '2022-04-20']
    max_april_20 = april_20.loc[april_20['total_price'] == april_20['total_price'].max()]
    print('Who sold the most on 4/20/2022?', max_april_20.iloc[0]['licensee_id'])
    print(f'${max_april_20.iloc[0]["total_price"]:,}')

    # Who sold the most in 2022?
    totals = stats.groupby('licensee_id').sum()
    max_total = totals.loc[totals['total_price'] == totals['total_price'].max()]
    print('Who sold the most in 2022?', max_total.iloc[0]['licensee_id'])

    # Who had the highest single day sales?
    max_sales = stats.loc[stats['total_price'] == stats['total_price'].max()]
    print('Who had the highest single day sales?', max_sales.iloc[0]['licensee_id'])
