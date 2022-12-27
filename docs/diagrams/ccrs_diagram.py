"""
CCRS Diagram
Copyright (c) 2022 Cannabis Data

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 12/26/2022
Updated: 12/26/2022
License: <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
"""
# Standard imports:
from urllib.request import urlretrieve

# External imports:
from diagrams import Cluster, Diagram
from diagrams.custom import Custom
from diagrams.firebase.develop import (
    Authentication,
    Firestore,
    Functions,
    Hosting,
    Storage,
)
from diagrams.gcp.compute import Run
from diagrams.generic.place import Datacenter
from diagrams.programming.flowchart import (
    Merge,
    MultipleDocuments,
)

# Download an image to be used into a Custom Node class
# rabbitmq_url = "https://jpadilla.github.io/rabbitmqapp/assets/img/icon.png"
# rabbitmq_icon = "rabbitmq.png"
# urlretrieve(rabbitmq_url, rabbitmq_icon)

with Diagram('CCRS Diagram', show=True) as diagram:
    with Cluster('Datasets'):
        datasets = [
            MultipleDocuments('SalesDetail'),
        ]

    datasets
    # queue = Custom("Message queue", rabbitmq_icon)
    # queue >> consumers >> Aurora("Database")



if __name__ == '__main__':

    # Render the diagram.
    diagram
    print('Diagram rendered to', diagram.filename)
