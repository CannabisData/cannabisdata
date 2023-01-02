"""
Curate CCRS Lab Results
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
from datetime import datetime
import os
from typing import Optional

# External imports:
from cannlytics.data.ccrs import (
    anonymize,
    get_datafiles,
    find_detections,
    format_test_value,
    unzip_datafiles,
)
from cannlytics.data.ccrs.constants import (
    CCRS_ANALYTES,
    CCRS_ANALYSES,
    CCRS_DATASETS,
)
from cannlytics.utils import convert_to_numeric
import pandas as pd


# Specify where your data lives.
DATA_DIR = 'D:\\data\\washington\\ccrs-2022-11-22\\ccrs-2022-11-22\\'
STATS_DIR = 'D:\\data\\washington\\ccrs-stats\\'


def curate_ccrs_lab_results(
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
    item_ids = list(results[item_key].unique())
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


def read_lab_results() -> pd.DataFrame:
    """Read CCRS lab results."""
    lab_results = pd.DataFrame()
    lab_result_files = get_datafiles(DATA_DIR, 'LabResult_')
    fields = CCRS_DATASETS['lab_results']['fields']
    parse_dates = CCRS_DATASETS['lab_results']['date_fields']
    usecols = list(fields.keys()) + parse_dates
    dtype = {k: v for k, v in fields.items() if v != 'datetime64'}
    dtype['TestValue'] = 'string' # Hot-fix
    for datafile in lab_result_files:
        data = pd.read_csv(
            datafile,
            sep='\t',
            encoding='utf-16',
            engine='python',
            parse_dates=parse_dates,
            dtype=dtype,
            usecols=usecols,
            on_bad_lines='skip',
        )
        lab_results = pd.concat([lab_results, data])
    values = lab_results['TestValue'].apply(convert_to_numeric)
    lab_results = lab_results.assign(TestValue=values)
    return lab_results


def save_dataset(
        data: pd.DataFrame,
        data_dir: str,
        name: str,
        ext: Optional[str] = 'xlsx',
    ) -> None:
    """Save a curated dataset, determining the number of datafiles
    (1 million per file) and saving each shard of the dataset."""
    if not os.path.exists(data_dir): os.makedirs(data_dir)
    file_count = round((len(data) + 1e6) / 1e6)
    for i in range(0, file_count):
        shard = data[0 + 1e6 * i: 1e6 + 1e6 * i]
        outfile = os.path.join(data_dir, f'{name}_{i}.{ext}')
        shard.to_excel(outfile, index=False)


# === Test ===
if __name__ == '__main__':

    print('Curating lab results...')
    start = datetime.now()

    # Unzip all CCRS datafiles.
    unzip_datafiles(DATA_DIR)

    # Read all lab results.
    lab_results = read_lab_results()

    # Curate all lab results.
    lab_results = curate_ccrs_lab_results(lab_results)

    # Save the curated lab results.
    lab_results_dir = os.path.join(STATS_DIR, 'lab_results')
    lab_results = anonymize(lab_results)
    save_dataset(lab_results, lab_results_dir)

    end = datetime.now()
    print('✓ Finished curating lab results in', end - start)
