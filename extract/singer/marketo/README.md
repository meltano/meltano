### Meltano Tap-Marketo

This is a Singer tap that produces JSON-formatted data following the Singer spec.  
https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#output

This tap:

- Pulls raw data from Marketo's REST API
- Extracts the following resources from Marketo:
  - Activity types
  - Activities
  - Leads  
- Outputs the JSON schema for each resource
- Incrementally pulls data based on the input state

#### Quick start
- `make build` This builds the image for use
- confirm you have the required env vars (as shown in the Makefile commands)
- `make run` This will automatically generate a valid keyfile and pull the data

###### Endpoint and Identity

The base URL contains the account id (a.k.a. Munchkin id) and is therefore unique for each Marketo subscription. Your base URL is found by logging into Marketo and navigating to the Admin > Integration > Web Services menu. It is labled as “Endpoint:” underneath the “REST API” section as shown in the following screenshots.

Identity is found directly below the endpoint entry.

http://developers.marketo.com/rest-api/base-url/

###### Client ID and Secret

These values are obtained by creating an app to integrate with Marketo.

http://developers.marketo.com/rest-api/authentication/

#### Manually creating the keyfile (optional)

Create a JSON file called config.json containing the Endpoint, Identity, Client ID, Client Secret and Start time.

```
{"endpoint": "your-endpoint",  
 "identity": "your-identity",  
 "client_id": "your-client_id",  
 "client_secret": "your-client-secret",  
 "start_time": "your_start_time"}  
 ```


tap-marketo can be run with:

`tap-marketo extract --config_path <path/to/config/file>`