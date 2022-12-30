"""
CCRS Sales by Licensee
Copyright (c) 2022 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/23/2022
Updated: 12/29/2022
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - Washington State Liquor and Cannabis Board (WSLCB)
    URL: <https://lcb.box.com/s/xseghpsq2t4i1musxj6mgd7b8rhxe7bm>

"""
# Standard imports:
import gc
import os
from typing import List, Optional
from zipfile import ZipFile

# External imports:
from cannlytics.data.ccrs.constants import (
    CCRS_ANALYTES,
    CCRS_ANALYSES,
    CCRS_DATASETS,
)
from cannlytics.utils import convert_to_numeric, rmerge, sorted_nicely
import pandas as pd


def get_ccrs_datafiles(
        data_dir: str,
        dataset: Optional[str] = '',
        desc: Optional[bool] = True,
    ) -> list:
    """Get all CCRS datafiles of a given type in a directory."""
    files = os.listdir(data_dir)
    datafiles = [f'{data_dir}/{f}/{f}/{f}.csv' for f in files if f.startswith(dataset)]
    datafiles = sorted_nicely(datafiles)
    if desc:
        datafiles.reverse()
    return datafiles


def unzip_ccrs(
        data_dir: str,
        verbose: Optional[bool] = True,
    ) -> None:
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


def merge_ccrs_datasets(
        df: pd.DataFrame,
        datafiles: List[str],
        dataset: str,
        on: Optional[str] = 'id',
        target: Optional[str] = '',
        how: Optional[str] = 'left',
        sep: Optional[str] = '\t',
        validate: Optional[str] = 'm:1',
        rename: Optional[dict] = None,
    ) -> pd.DataFrame:
    """Merge a supplemental CCRS dataset to an existing dataset."""
    n = len(df)
    augmented = pd.DataFrame()
    fields = CCRS_DATASETS[dataset]['fields']
    parse_dates = CCRS_DATASETS[dataset]['date_fields']
    usecols = list(fields.keys()) + parse_dates
    dtype = {k: v for k, v in fields.items() if v != 'datetime64'}
    if dtype.get('IsDeleted'):
        dtype['IsDeleted'] = 'string' # Hot-fix for ValueError.
    if dtype.get('UnitWeightGrams'):
        dtype['UnitWeightGrams'] = 'string'
    for datafile in datafiles:
        supplement = pd.read_csv(
            datafile,
            sep=sep,
            encoding='utf-16',
            engine='python',
            parse_dates=parse_dates,
            dtype=dtype,
            usecols=usecols,
            on_bad_lines='skip',
        )
        supplement.rename(columns=rename, axis=1)
        if dataset == 'lab_results':
            supplement = format_ccrs_lab_results(supplement)
        match = rmerge(
            df,
            supplement,
            on=on,
            how=how,
            validate=validate,
        )
        matched = match.loc[~match[target].isna()]
        augmented = pd.concat([augmented, matched]) 
        if len(augmented) == n:
            break
    return augmented


def format_value(v, key='TestValue'):
    try:
        convert_to_numeric(v.iloc[0][key])
    except:
        return None


def format_ccrs_lab_results(
        df: pd.DataFrame,
        results: pd.DataFrame,
        item_key: Optional[str] = 'InventoryId',
    ) -> pd.DataFrame:
    """Format CCRS lab results to merge into another dataset."""
    formatted = []
    analyte_data = results['TestName'].map(CCRS_ANALYTES).values.tolist()
    results = results.join(pd.DataFrame(analyte_data))
    results['type'] = results['type'].map(CCRS_ANALYSES)
    item_ids = list(df[item_key].unique())
    for item_id in item_ids:
        item_results = results.loc[results[item_key].astype(str) == item_id]
        delta_9_thc = item_results.loc[(item_results.key == 'delta_9_thc')]
        thca = item_results.loc[(item_results.key == 'thca')]
        total_thc = item_results.loc[(item_results.key == 'total_thc')]
        cbd = item_results.loc[(item_results.key == 'cbd')]
        cbda = item_results.loc[(item_results.key == 'cbda')]
        total_cbd = item_results.loc[(item_results.key == 'total_cbd')]
        moisture_content = item_results.loc[(item_results.key == 'moisture_content')]
        water_activity = item_results.loc[(item_results.key == 'water_activity')]
        values = item_results.iloc[0].to_dict()
        [values.pop(key) for key in ['TestName', 'TestValue']]
        entry = {
            **values,
            'delta_9_thc': format_value(delta_9_thc),
            'thca': format_value(thca),
            'total_thc': format_value(total_thc),
            'cbd': format_value(cbd),
            'cbda': format_value(cbda),
            'total_cbd': format_value(total_cbd),
            'moisture_content': format_value(moisture_content),
            'water_activity': format_value(water_activity),
        }
        
        # Determine `status`.
        statuses = list(item_results['LabTestStatus'].unique())
        if 'Fail' in statuses:
            entry['status'] = 'Fail'
        else:
            entry['status'] = 'Pass'

        # TODO: Format lab results dataframe
        # - status
        # - detected_pesticides
        # - detected_solvents
        # - detected_metals

        # Record the lab results for the item.
        formatted.append(entry)
    
    # Return the lab results.
    return pd.DataFrame(formatted)


def calc_daily_sales(
        df: pd.DataFrame,
        stats: dict,
    ) -> dict:
    """Calculate sales by licensee by day.
    Note: The absolute value of the `Discount` is used.
    """
    group = ['LicenseeId', 'SaleDate']
    daily = df.groupby(group, as_index=False).sum()
    for _, row in daily.iterrows():
        licensee_id = row['LicenseeId']
        date = row['SaleDate'].isoformat()[:10]
        licensee_data = stats.get(licensee_id, {})
        date_data = licensee_data.get(date, {})
        licensee_data[date] = {
            'total_price': date_data.get('total_price', 0) + row['UnitPrice'],
            'total_discount': date_data.get('total_discount', 0) + abs(row['Discount']),
            'total_sales_tax': date_data.get('total_sales_tax', 0) + row['SalesTax'],
            'total_other_tax': date_data.get('total_other_tax', 0) + row['OtherTax'],
        }
        stats[licensee_id] = licensee_data
    return stats


def save_licensee_items_by_month(
        df: pd.DataFrame,
        data_dir: str,
        item_type: Optional[str] = 'sales',
        subset: Optional[str] = '',
        parse_dates: Optional[list] =None,
        dtype: Optional[dict] = None,
        verbose: Optional[bool] = True,
    ) -> None:
    """Save items by licensee by month to licensee-specific directories.
    Note: Datafiles must be under 1 million items.
    """
    licensees = list(df['LicenseeId'].unique())
    for licensee_id in licensees:
        licensee_dir = os.path.join(data_dir, licensee_id)
        if not os.path.exists(licensee_dir): os.makedirs(licensee_dir)
        licensee_items = df.loc[df['LicenseeId'] == licensee_id]
        months = list(licensee_items['month'].unique())
        for month in months:
            outfile = f'{licensee_dir}/{item_type}-{licensee_id}-{month}.xlsx'
            month_items = licensee_items.loc[licensee_items['month'] == month]
            try:
                existing_items = pd.read_excel(
                    outfile,
                    parse_dates=parse_dates,
                    dtype=dtype,
                )
                month_items = pd.concat([existing_items, month_items])
                month_items[subset] = month_items[subset].astype(str)
                month_items.drop_duplicates(subset=subset, keep='last', inplace=True)
            except FileNotFoundError:
                pass
            month_items.to_excel(outfile, index=False)
            if verbose:
                print('Saved', licensee_id, month, 'items:', len(month_items))


def save_stats_by_month(
        df: pd.DataFrame,
        data_dir: str,
        series: str,
    ) -> None:
    """Save given series statistics by month to given data directory."""
    df['month'] = df['date'].apply(lambda x: x[:7])
    months = list(df['month'].unique())
    for month in months:
        outfile = f'{data_dir}/{series}-{month}.xlsx'
        month_stats = df.loc[df['month'] == month]
        month_stats.to_excel(outfile, index=False)


def stats_to_df(stats: dict[dict]) -> pd.DataFrame:
    """Compile statistics from a dictionary of dictionaries into a DataFrame."""
    data = []
    for licensee_id, dates in stats.items():
        for date, values in dates.items():
            data.append({
                'licensee_id': licensee_id,
                'date': date,
                **values,
            })
    return pd.DataFrame(data)


# === Test ===
if __name__ == '__main__':

    # === Data Collection ===

    # Specify where your data lives.
    DATA_DIR = 'D:\\data\\washington\\ccrs-2022-11-22\\ccrs-2022-11-22\\'
    STATS_DIR = 'D:\\data\\washington\\ccrs-stats\\'

    # Create stats directory if it doesn't already exist.
    licensees_dir = os.path.join(STATS_DIR, 'licensee_stats')
    sales_dir = os.path.join(STATS_DIR, 'sales')
    if not os.path.exists(STATS_DIR): os.makedirs(STATS_DIR)
    if not os.path.exists(licensees_dir): os.makedirs(licensees_dir)
    if not os.path.exists(sales_dir): os.makedirs(sales_dir)

    # Unzip all CCRS datafiles.
    unzip_ccrs(DATA_DIR)

    # Define all sales fields.
    # Note: `IsDeleted` throws a ValueError if it's a bool.
    fields = CCRS_DATASETS['sale_details']['fields']
    date_fields = CCRS_DATASETS['sale_details']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}
    item_types['IsDeleted'] = 'string'

    # Define all sales headers fields.
    supp_fields = CCRS_DATASETS['sale_headers']['fields']
    supp_date_fields = CCRS_DATASETS['sale_headers']['date_fields']
    supp_cols = list(supp_fields.keys()) + supp_date_fields
    supp_types = {k: supp_fields[k] for k in supp_fields if k not in supp_date_fields}

    # === Data Curation ===

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
    licensees.rename(columns=columns, inplace=True)

    # Iterate over all sales items files to calculate stats.
    daily_licensee_sales = {}
    sales_items_files = get_ccrs_datafiles(DATA_DIR, 'SalesDetail_')
    inventory_files = get_ccrs_datafiles(DATA_DIR, 'Inventory_')
    product_files = get_ccrs_datafiles(DATA_DIR, 'Product_')
    lab_result_files = get_ccrs_datafiles(DATA_DIR, 'LabResult_')
    for i, datafile in enumerate(sales_items_files):
        datafile_name = datafile.split('/')[-1]

        # DEV: Stop iterating early.
        if i > 0:
            continue

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
        items = items.loc[
            (items['IsDeleted'] != 'True') &
            (items['IsDeleted'] != True)
        ]

        # Iterate over the sales headers until all items have been augmented.
        # Note: There is probably a clever way to reduce the number of times
        # that the headers are read. Currently reads all sale headers from
        # current to earliest then reads earliest to current for the
        # 2nd half to try to reduce unnecessary reads.
        if i < len(sales_items_files) / 2:
            sale_headers_files = get_ccrs_datafiles(DATA_DIR, 'SaleHeader_')
        else:
            sale_headers_files = get_ccrs_datafiles(DATA_DIR, 'SaleHeader_', desc=False)
        items = merge_ccrs_datasets(
            items,
            sale_headers_files,
            dataset='sale_headers',
            on='SaleHeaderId',
            target='LicenseeId',
            how='left',
            validate='m:1',
        )
        print('Merged sale header data for', datafile_name)

        # Merge items with licensee data.
        items = rmerge(
            items,
            licensees,
            on='LicenseeId',
            how='left',
            validate='m:1',
        )
        print('Merged licensee data for', datafile_name)

        # Merge with inventory data to get `ProductId`.
        items = merge_ccrs_datasets(
            items,
            inventory_files,
            dataset='inventory',
            on='InventoryId',
            target='ProductId',
            how='left',
            validate='m:1',
            rename={
               'CreatedDate': 'inventory_created_at',
               'updatedDate': 'inventory_updated_at',
               'ExternalIdentifier': 'inventory_external_id',
               'LicenseeId': 'producer_licensee_id',
            },
        )
        print('Merged inventory data for', datafile_name)

        # Merge items with product data.
        items = merge_ccrs_datasets(
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
        print('Merged product data for', datafile_name)

        # TODO: Get lab results with `InventoryId`.
        items = merge_ccrs_datasets(
            items,
            lab_result_files,
            dataset='lab_results',
            on='InventoryId',
            target='total_thc',
            how='left',
            validate='m:1',
            rename={
               'CreatedDate': 'lab_result_created_at',
               'UpdatedDate': 'lab_result_updated_at',
               'ExternalIdentifier': 'lab_result_external_id',
               'LicenseeId': 'producer_licensee_id',
            },
        )

        # At this stage, sales by licensee by day can be incremented.
        # daily_licensee_sales = calc_daily_sales(items, daily_licensee_sales)

        # Save augmented sales to licensee-specific files by month.
        # items['month'] = items['SaleDate'].apply(lambda x: x.isoformat()[:7])
        # save_licensee_items_by_month(
        #     items,
        #     licensees_dir,
        #     subset='SaleDetailId',
        #     # FIXME: Pass item date columns and types.
        #     # parse_dates=list(set(date_fields + supp_date_fields)),
        #     # dtype={**supp_types, **item_types},
        # )
    
    # === Data Analysis ===

    # Optional: Add licensee data.

    # Compile the statistics.
    stats = stats_to_df(daily_licensee_sales)

    # Save the compiled statistics.
    stats.to_excel(f'{sales_dir}/sales-by-licensee.xlsx', index=False)

    # Save the statistics by month.
    # save_stats_by_month(stats, sales_dir, 'sales-by-licensee')

    # TODO: Calculate and save aggregate statistics.
