"""
Upload CCRS Statistics
Copyright (c) 2022-2023 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/4/2022
Updated: 1/7/2023
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB
    URL: <https://lcb.app.box.com/s/xseghpsq2t4i1musxj6mgd7b8rhxe7bm>

Command-line Usage:

    python tools/ccrs/upload_ccrs_stats.py

"""
# Standard imports:
import os

# External imports:
from cannlytics import firebase
from cannlytics.data.ccrs import CCRS_DATASETS
from cannlytics.utils import snake_case, sorted_nicely
from dotenv import dotenv_values
import pandas as pd


def upload_ccrs_stats(data_dir, stats_dir):
    """Calculate CCRS statistics and upload the stats to Firestore."""
    # Initialize Firebase.
    try:
        config = dotenv_values('../.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        config = dotenv_values('./.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
    db = firebase.initialize_firebase()

    # Upload licensee data.
    # TODO: Upload augmented licensee data instead!
    fields = CCRS_DATASETS['licensees']['fields']
    date_fields = CCRS_DATASETS['licensees']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}
    data = pd.read_csv(
        f'{data_dir}/Licensee_0/Licensee_0/Licensee_0.csv',
        sep='\t',
        encoding='utf-16',
        parse_dates=date_fields,
        usecols=item_cols,
        dtype=item_types,
    )
    data.rename(columns=lambda x: snake_case(x), inplace=True)
    docs = data.to_dict('records')
    refs = [f'data/ccrs/licensees/{doc["licensee_id"]}' for doc in docs]
    firebase.update_documents(docs, refs, database=db)

    # Upload inventory data.
    inventory_dir = os.path.join(stats_dir, 'inventory')
    inventory_files = sorted_nicely(os.listdir(inventory_dir))
    fields = CCRS_DATASETS['inventory']['fields']
    date_fields = CCRS_DATASETS['inventory']['date_fields']
    item_cols = list(fields.keys()) + date_fields
    item_types = {k: fields[k] for k in fields if k not in date_fields}
    for datafile in inventory_files:
        print('Uploading:', datafile)
        data = pd.read_csv(
            datafile,
            sep='\t',
            encoding='utf-16',
            parse_dates=date_fields,
            usecols=item_cols,
            dtype=item_types,
        )
        data.rename(columns=lambda x: snake_case(x), inplace=True)
        docs = data.to_dict('records')
        refs = [f'data/ccrs/inventory/{doc["inventory_id"]}' for doc in docs]
        firebase.update_documents(docs, refs, database=db)
    
    # Upload lab result data.
    lab_results_dir = os.path.join(stats_dir, 'lab_results')
    results_file = os.path.join(lab_results_dir, 'inventory_lab_results_0.xlsx')
    data = pd.read_excel(results_file)
    docs = data.to_dict('records')
    refs = [f'data/ccrs/inventory_lab_results/{doc["inventory_id"]}' for doc in docs]
    firebase.update_documents(docs, refs, database=db)


    # TODO: Upload sales data.


    # TODO: Upload plant data.


    # TODO: Upload additional datasets:
    # - products
    # - inventory adjustments
    # - plant destructions / plant transfers
    # - strains

    # TODO: Upload metadata about the datasets.


# === Test ===
if __name__ == '__main__':

    # Specify where your data lives.
    base = 'D:\\data\\washington\\'
    DATA_DIR = f'{base}\\CCRS PRR (12-7-22)\\CCRS PRR (12-7-22)\\'
    STATS_DIR = f'{base}\\ccrs-stats\\'

    # Upload CCRS stats to Firestore.
    upload_ccrs_stats(DATA_DIR, STATS_DIR)
    print('Uploaded CCRS stats to Firestore.')
