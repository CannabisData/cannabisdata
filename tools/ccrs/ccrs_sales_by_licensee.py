"""
CCRS Sales by Licensee
Copyright (c) 2022 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/23/2022
Updated: 12/31/2022
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - Washington State Liquor and Cannabis Board (WSLCB)
    URL: <https://lcb.box.com/s/xseghpsq2t4i1musxj6mgd7b8rhxe7bm>

"""
# Standard imports:
import os
from typing import List, Optional
from zipfile import ZipFile

# External imports:
from cannlytics.data.ccrs.constants import (
    CCRS_ANALYTES,
    CCRS_ANALYSES,
    CCRS_DATASETS,
)
from cannlytics.utils import (
    convert_to_numeric,
    rmerge,
    sorted_nicely,
)
import pandas as pd


# Specify where your data lives.
DATA_DIR = 'D:\\data\\washington\\ccrs-2022-11-22\\ccrs-2022-11-22\\'
STATS_DIR = 'D:\\data\\washington\\ccrs-stats\\'


def get_ccrs_datafiles(
        data_dir: str,
        dataset: Optional[str] = '',
        desc: Optional[bool] = True,
    ) -> list:
    """Get all CCRS datafiles of a given type in a directory."""
    datafiles = sorted_nicely([
        os.path.join(data_dir, f, f, f + '.csv')
        for f in os.listdir(data_dir) if f.startswith(dataset)
    ])
    if desc:
        datafiles.reverse()
    return datafiles


def unzip_ccrs(
        data_dir: str,
        verbose: Optional[bool] = True,
    ) -> None:
    """Unzip all CCRS datafiles in a given directory."""
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
        on_bad_lines: Optional[str] = 'skip',
    ) -> pd.DataFrame:
    """Merge a supplemental CCRS dataset to an existing dataset.
    Note: `IsDeleted` and `UnitWeightGrams` are treated as strings.
    Lab results cannot be split between datafiles.
    """
    n = len(df)
    augmented = pd.DataFrame()
    fields = CCRS_DATASETS[dataset]['fields']
    parse_dates = CCRS_DATASETS[dataset]['date_fields']
    usecols = list(fields.keys()) + parse_dates
    dtype = {k: v for k, v in fields.items() if v != 'datetime64'}
    # FIXME: These fields throw `ValueError` if not strings.
    if dtype.get('IsDeleted'):
        dtype['IsDeleted'] = 'string'
    if dtype.get('UnitWeightGrams'):
        dtype['UnitWeightGrams'] = 'string'
    if dtype.get('TestValue'):
        dtype['TestValue'] = 'string'
    for datafile in datafiles:
        supplement = pd.read_csv(
            datafile,
            sep=sep,
            encoding='utf-16',
            engine='python',
            parse_dates=parse_dates,
            dtype=dtype,
            usecols=usecols,
            on_bad_lines=on_bad_lines,
        )
        if rename is not None:
            supplement.rename(rename, axis=1, inplace=True)
        # FIXME: Handle lab results that may be split between datafiles.
        if dataset == 'lab_results':
            supplement = format_lab_results(df, supplement)
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


def format_test_value(tests, compound, value_key='TestValue'):
    """Format a lab result test value from a DataFrame of tests."""
    value = tests.loc[(tests.key == compound)]
    try:
        return convert_to_numeric(value.iloc[0][value_key])
    except:
        return None


def find_detections(
        tests,
        analysis,
        analysis_key='type',
        analyte_key='key',
        value_key='TestValue',
    ) -> List[str]:
    """Find compounds detected for a given analysis from given tests."""
    df = tests.loc[tests[analysis_key] == analysis]
    if df.empty:
        return []
    df.loc[:, value_key] = df[value_key].apply(convert_to_numeric)
    detected = df.loc[df[value_key] > 0]
    if detected.empty:
        return []
    return detected[analyte_key].to_list()


def format_lab_results(
        df: pd.DataFrame,
        results: pd.DataFrame,
        item_key: Optional[str] = 'InventoryId',
        analysis_name: Optional[str] = 'TestName',
        analysis_key: Optional[str] = 'TestValue',
    ) -> pd.DataFrame:
    """Format CCRS lab results to merge into another dataset."""

    # Curate lab results.
    analyte_data = results[analysis_name].map(CCRS_ANALYTES).values.tolist()
    results = results.join(pd.DataFrame(analyte_data))
    results['type'] = results['type'].map(CCRS_ANALYSES)

    # Find lab results for each item.
    formatted = []
    item_ids = list(df[item_key].unique())
    for item_id in item_ids:
        item_results = results.loc[results[item_key].astype(str) == item_id]
        if item_results.empty:
            continue

        # Map certain test values.
        values = item_results.iloc[0].to_dict()
        [values.pop(key) for key in [analysis_name, analysis_key]]
        entry = {
            **values,
            'analyses': list(item_results['type'].unique()),
            'delta_9_thc': format_test_value(item_results, 'delta_9_thc'),
            'thca': format_test_value(item_results, 'thca'),
            'total_thc': format_test_value(item_results, 'total_thc'),
            'cbd': format_test_value(item_results, 'cbd'),
            'cbda': format_test_value(item_results, 'cbda'),
            'total_cbd': format_test_value(item_results, 'total_cbd'),
            'moisture_content': format_test_value(item_results, 'moisture_content'),
            'water_activity': format_test_value(item_results, 'water_activity'),
        }

        # Determine `status`.
        statuses = list(item_results['LabTestStatus'].unique())
        if 'Fail' in statuses:
            entry['status'] = 'Fail'
        else:
            entry['status'] = 'Pass'
        
        # Determine detected contaminants.
        entry['pesticides'] = find_detections(item_results, 'pesticides')
        entry['residual_solvents'] = find_detections(item_results, 'residual_solvent')
        entry['heavy_metals'] = find_detections(item_results, 'heavy_metals')

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


def ccrs_sales_by_licensee():
    """Calculate CCRS licensee sales statistics."""

    # === Data Collection ===
    
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
    licensees.rename(columns, axis=1, inplace=True)

    # Iterate over all sales items files to calculate stats.
    daily_licensee_sales = {}
    sales_items_files = get_ccrs_datafiles(DATA_DIR, 'SalesDetail_')
    inventory_files = get_ccrs_datafiles(DATA_DIR, 'Inventory_')
    product_files = get_ccrs_datafiles(DATA_DIR, 'Product_')
    lab_result_files = get_ccrs_datafiles(DATA_DIR, 'LabResult_')
    for i, datafile in enumerate(sales_items_files):
        print('Augmenting:', datafile)

        # DEV: Stop iterating early.
        # if i > 0:
        #     continue

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
        print('Merging sale header data...')
        items = merge_ccrs_datasets(
            items,
            sale_headers_files,
            dataset='sale_headers',
            on='SaleHeaderId',
            target='LicenseeId',
            how='left',
            validate='m:1',
        )
        print('Merged sale header data.')

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

        # Merge with inventory data to get `ProductId`.
        print('Merging inventory data...')
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
        print('Merged inventory data.')

        # Merge items with product data.
        print('Merging product data...')
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
        print('Merged product data.')

        # Get lab results with `InventoryId`.
        print('Merging lab result data...')
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
        print('Merged lab result data.')

        # At this stage, sales by licensee by day can be incremented.
        print('Updating statistics...')
        daily_licensee_sales = calc_daily_sales(items, daily_licensee_sales)

        # Save augmented sales to licensee-specific files by month.
        items['month'] = items['SaleDate'].apply(lambda x: x.isoformat()[:7])
        save_licensee_items_by_month(
            items,
            licensees_dir,
            subset='SaleDetailId',
            verbose=False,
            # FIXME: Pass item date columns and types.
            # parse_dates=list(set(date_fields + supp_date_fields)),
            # dtype={**supp_types, **item_types},
        )
        print('Updated statistics and licensee items.')
    
    # === Data Analysis ===

    # Optional: Add licensee data.

    # Compile the statistics.
    print('Compiling licensee sales statistics...')
    stats = stats_to_df(daily_licensee_sales)

    # Save the compiled statistics.
    stats.to_excel(f'{sales_dir}/sales-by-licensee.xlsx', index=False)

    # Save the statistics by month.
    save_stats_by_month(stats, sales_dir, 'sales-by-licensee')

    # TODO: Calculate and save aggregate statistics.

    print('✓ Finished calculating CCRS licensee sales statistics.')


# === Test ===
if __name__ == '__main__':
    ccrs_sales_by_licensee()
