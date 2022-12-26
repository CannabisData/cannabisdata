"""
Upload CCRS Statistics
Copyright (c) 2022 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/4/2022
Updated: 12/4/2022
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>

Data Source:

    - WSLCB
    URL: <https://lcb.app.box.com/s/xseghpsq2t4i1musxj6mgd7b8rhxe7bm>

Command-line Usage:

    python tools/upload_ccrs_stats.py

"""
# Standard imports:
import os

# External imports:
from cannlytics import firebase
from dotenv import dotenv_values


def upload_ccrs_stats():
    """Calculate CCRS statistics and upload the stats to Firestore.
    """
    raise NotImplementedError


# === Test ===
if __name__ == '__main__':

    # Set Firebase credentials.
    try:
        config = dotenv_values('../.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        config = dotenv_values('./.env')
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    # Upload CCRS stats to Firestore.
    upload_ccrs_stats()
    print('Uploaded CCRS stats to Firestore.')
