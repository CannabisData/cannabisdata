# Authentication

The Cannabis Data API utilizes API keys for authentication.

## API Keys

An API key identifies a particular user, granting programmatic use at the same level of permission as the user. User API keys are encrypted using a provider's secret key. The secret key is specific to the provider, such as the Cannabis Data hosted solution. So, only that provider can provide services to the user with the credentials provided. [Google Secret Manager](https://cloud.google.com/secret-manager) is used to protect your user API keys. Cannabis Data does not store API keys, instead HMACs are used to securely represent API key claims.

!!! danger "Your API key is observable if you use HTTP, so please use HTTPS when you make requests to the Cannabis Data API."

!!! tip "We strongly recommend that you encrypt your API keys in your data store and in memory when working with them except when you need to access them to access the service."

#### Expiration

Your API key will expire after a set mount of time, 6 months by default, but you can set the expiration date as you desire.

#### Customer Holding

You hold your API key, we do not have your API key and can not generate it if it is lost. However, you can easily delete lost API keys and create new API keys to use in their place.

## API Requests

You can make requests through the API passing your API key as a bearer token in the authorization header. Below is an example in Python reading an API key from a local `.env` file.

=== "Python"

    ```py

    import os
    from dotenv import load_dotenv

    # Load your API key.
    load_dotenv('.env')
    API_KEY = os.getenv('CANNABIS_DATA_API_KEY')

    # Pass your API key through the authorization header as a bearer token.
    HEADERS = {
        'Authorization': 'Bearer %s' % API_KEY,
        'Content-type': 'application/json',
    }
    ```


=== "Node.js"

    ```js
    const axios = require('axios');
    require('dotenv').config();

    // Pass API key through the authorization header as a bearer token.
    const apiKey = process.env.CANNABIS_DATA_API_KEY;
    const options = {
      headers: { 'Authorization' : `Bearer ${apiKey}` }
    };
    ```
