# Cannabis Data API

The Cannabis Data API allows users to use Cannabis Data programmatically. The API endpoints handle authentication, error handling, and identifying the precise logic to perform.

- [Getting Started with the API](#getting-started)
- [Data API Endpoints](#data-api-endpoints)
- [Stats API Endpoints](#stats-api-endpoints)
- [Organizations API Endpoints](#organizations-api-endpoints)
- [Users API Endpoints](#users-api-endpoints)

## Getting Started with the API <a name="getting-started"></a>

Getting started making requests to the Cannlytics API can be done in 3 quick steps.

1. First, [create a Cannlytics account](https://console.cannlytics.com/account/sign-up).
2. Second, [create an API key](https://console.cannlytics.com/settings/api).
3. Third, begin making requests to the Cannlytics API with your API Key in an `Authorization: Bearer <token>` header.

For advanced usage, you can manage your authentication session with the `auth` endpoints in the table below.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\auth\authenticate` | `POST` | Create an authorized session. |
| `\auth\login` | `POST` | Sign into your Firebase user account. |
| `\auth\logout` | `POST` | Sign out of your Firebase user account and end your authorized session. |

<!-- TODO: Document the following endpoints:
create-key
delete-key
get-keys
-->

## Data API Endpoints <a name="data-api-endpoints"></a>

You can get cannabis data through the `data` API endpoints described below.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\data\licenses` | `GET` | Get the data of cannabis licenses. Append a URL-escaped `<license_number>` or `<license_id>` to query a specific license. |

## Stats API Endpoints <a name="stats-api-endpoints"></a>

You can interface with various statistical models through the `stats` API endpoints listed in the table below. The `stats` API endpoints are clever mechanisms for you to capitalize on state-of-the-line statistics privately in the cloud. 

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\stats\basket` | `GET`, `POST` | *Coming Soon* |
| `\stats\forecast` | `GET`, `POST` | *Coming Soon* |
| `\stats\impulse` | `GET`, `POST` | *Coming Soon* |

## Organizations API Endpoints <a name="organizations-api-endpoints"></a>

You can manage your organizations through the `organizations` API endpoints listed in the table below.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\organizations\<organization_id>` | `GET`, `POST` | Get an organization's details. Must be an organization owner or authorized team member to change the organization details. |
| `\organizations\<organization_id>\settings` | `GET`, `POST` | Get an organization's settings. Must be the organization's owner or team member to get the settings and must be the owner or an authorized team member to change the settings. |
| `\organizations\<organization_id>\team` | `GET` | Get an organization's team. |
| `\organizations\<organization_id>\team\<user_ud>` | `GET` | Get an organization team member details. |

## Users API Endpoints <a name="users-api-endpoints"></a>

You can manage your user account through the `users` API endpoints listed in the table below.

| Endpoint | Methods | Description |
| -------- | ------- | ----------- |
| `\users\<user_id>` | `GET`, `POST` | Get your user details. |
| `\users\<user_id>\logs` | `GET`, `POST` | Get your user logs. Append a `log_id` path to query a specific log. |
| `\users\<user_id>\settings` | `GET`, `POST` | Get your user settings. |
