## Sample: AAD-protected Flask API + Power BI Desktop custom connector

The Flask app uses [python-jose-cryptodome](https://pypi.org/project/python-jose-cryptodome/) to decode incoming Azure AD bearer tokens created using OAuth2 flows like [auth code flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow) or [client credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow).

The Power BI custom connector uses auth_code flow for its AAD token.

### Setup:

* Register an application in Azure AD and obtain the app_id and tenant_id. You'll also need to configure a redirect URL value of https://oauth.powerbi.com/views/oauthredirect.html

* Add your app_id to [pbi-connector/client_id](pbi-connector/client_id) as the only contents of that file

* In [pbi-connector/MyGraph.pq](pbi-connector/MyGraph.pq) replace TENANT-ID with your tenant_id from Azure AD app registration

* Modify [flask-oauth-azure/.env](flask-oauth-azure/.env) with your tenant_id

* You'll need Visual Studio + [Power Query SDK](https://marketplace.visualstudio.com/items?itemName=Dakahn.PowerQuerySDK) to build the pbi-connector project

* The Flask app runs in Docker... you can run it directly on your laptop, but whyyy

### Build and run the API

* Run [build.sh](build.sh) to build the Docker image

* Run [run.sh](run.sh) to run the image, the server is visible at http://localhost:5000. Use the /data secure endpoint to retrieve data

### Build and deploy the Power BI connector

* Build the pbi-connector project in Visual Studio and use F5 debugging to test it within VS

* [Deploy the PBI custom connector .mez file](https://github.com/microsoft/DataConnectors/blob/master/docs/m-extensions.md#build-and-deploy-from-visual-studio)

* [Configure and run the connector](https://github.com/microsoft/DataConnectors)