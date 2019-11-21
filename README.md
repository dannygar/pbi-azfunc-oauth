# Sample: AAD-protected Azure Function API + Power BI Desktop Custom connector

This code example demonstrates how to secure Power BI Desktop while connecting to an Azure function API with Azure AD when   the Power BI desktop uses PBI Custom Connector to consume the secure data via a Web API. The Web API is written using Python.

This readme walks you through the steps of setting this code up in your Azure subscription.

The Azure Function API uses [Azure Samples for Python WebAPI](https://github.com/Azure-Samples/ms-identity-python-webapi-azurefunctions) as a based app to demonstrate using OAuth2 flows like [auth code flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow) or [client credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow).

The Power BI custom connector uses auth_code flow for its AAD token.

## Prerequisites
1. You must have Visual Studio 2017/9 and Visual Studio Code installed
2. You must have Visual Studio + [Power Query SDK](https://marketplace.visualstudio.com/items?itemName=Dakahn.PowerQuerySDK) to build the pbi-connector project
3. You must have Azure Functions core tools installed `npm install -g azure-functions-core-tools`
4. Azure functions VSCode extension (https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)

## Register an AAD App:

Reference: [How to register an app](https://docs.microsoft.com/en-nz/azure/active-directory/develop/quickstart-register-app)

The Azure function acts as a WebAPI. There are a few things to know here.
1. The function app will run on `http://localhost:7071` when you test it locally.
2. The function app will run on `https://<yourpythonfunction>.azurewebsites.net` when you run it deployed in azure
3. The function exposes an API with app id uri `https://<yourpythonfunction>.<tenant>.onmicrosoft.com`

Note that all these values are configurable to your liking, and they are reflected in the `__app__/bootstrapFunction/secureFlaskApp.py` file.

Since this function will serve as a AAD protected Web API, any client that understands standard openid connect flows will work. This sample shows how to use Power BI as a client app. The usual consent grant principals apply. 

Reference: [Azure Active Directory consent framework](https://docs.microsoft.com/en-us/azure/active-directory/develop/consent-framework)

To keep things simple, we will reuse the same app registration as both the client, and the API. This eliminates any need to provide explicit consent. For our code example here, the client will use [auth code flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow), for which we will also need a client secret. We are trying to mimic a web app calling this API, and a web app can act as a confidential client.

To setup the app, you can use the below azure CLI script. Note the placeholders demarcated in `<..>` brackets. Make sure to replace them with your environment specific values.

``` SHELL
az ad app create --display-name "FuncAPI" --credential-description "funcapi" --password "p@ssword1" --reply-urls "http://localhost:7071", "https://<funcapi>.azurewebsites.net" --identifier-uris "https://funcapi.<tenantname>.onmicrosoft.com"
```

For the above registered app, get the app ID
``` SHELL
az ad app list --query "[?displayName == 'FuncAPI'].appId"
```
and save the password as you will use it later as the client's *client_secret*.

Also get your tenant ID
``` SHELL
az account show --query "tenantId"
```


Update your `__app__/bootstrapFunction/secureFlaskApp.py` with the values per your app registration. Specifically, update the below lines.

``` Python
API_AUDIENCE = "https://funcapi.<tenantname>.onmicrosoft.com"
TENANT_ID = "<tenantid>"
```

``` Power BI Connector
* Add your app_id to [pbi-connector/appsettings.json](pbi-connector/appsettings.json) 
* Add your client_secret to [pbi-connector/appsettings.json](pbi-connector/appsettings.json) 


## Test your function - locally

 1. With the project open in VSCode, just hit F5, or you can also run `func host start` from the CLI.
 2. You will need an access token to call this function. In order to get the access token, open browser in private mode and visit
 ```
 https://login.microsoftonline.com/<tenantname>.onmicrosoft.com/oauth2/v2.0/authorize?response_type=code&client_id=<appid>&redirect_uri=http://localhost:7071/&scope=openid
```

This will prompt you to perform authentication and consent, and it will return a code in the query string. 
Use that code in the following request to get an access token, remember to put in the code and client secret.
I am using the client secret of `p@ssword1` as I setup in my scripts above. In production environments, you want this to be more complex.

``` SHELL
curl -X POST \
  https://login.microsoftonline.com/<tenantname>.onmicrosoft.com/oauth2/v2.0/token \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Host: login.microsoftonline.com' \
  -H 'accept-encoding: gzip, deflate' \
  -H 'cache-control: no-cache' \
  -d 'redirect_uri=http%3A%2F%2Flocalhost:7071&client_id=<appid>&grant_type=authorization_code&code=<put code here>&client_secret=p@ssword1&scope=https%3A%2F%funcapi.<tenantname>.onmicrosoft.com%2F/user_impersonation'
  ```
 
 3. Once you get the access token, make a GET request to `http://localhost:7071/api/user` with the access token as a Authorization Bearer header. Verify that you get an output similar to the below. The values marked as ..removed.. will have actual values in your output.

 ``` JSON
{
    "aud": "https://funcapi.<tenantname>.onmicrosoft.com",
    "iss": "https://sts.windows.net/<tenantid>/",
    "iat": 1571732525,
    "nbf": 1571732525,
    "exp": 1571736425,
    "acr": "1",
    "aio": "..removed..",
    "amr": [
        "pwd"
    ],
    "appid": "..removed..",
    "appidacr": "1",
    "email": "..removed..",
    "family_name": "..removed..",
    "given_name": "..removed..",
    "idp": "..removed..",
    "ipaddr": "..removed..",
    "name": "..removed..",
    "oid": "..removed..",
    "scp": "user_impersonation",
    "sub": "..removed..",
    "tid": "..removed..",
    "unique_name": "..removed..",
    "uti": "..removed..",
    "ver": "1.0"
}
```

 4. You can then test the second API endpoint that should return the JSON formatted list of people names and ages: `http://localhost:7071/api/data` with the access token as a Authorization Bearer header. Verify that you get an output similar to the below. 

 ``` JSON
{
    "people": [
        {
            "age": 47,
            "id": 1,
            "name": "Josh"
        },
        {
            "age": 45,
            "id": 2,
            "name": "Adam"
        },
        {
            "age": 33,
            "id": 3,
            "name": "Fred"
        }
    ]
}
```


 ## Test your function - in Azure

 1. Go ahead and create a function app in azure, ensure that you pick python as it's runtime.
 2. Choose to deploy the function
 3. You will need an access token to call this function. In order to get the access token, open browser in private mode and visit
```
https://login.microsoftonline.com/<tenantname>.onmicrosoft.com/oauth2/v2.0/authorize?response_type=code&client_id=<appid>&redirect_uri=https://<yourpythonfunction>.azurewebsites.net/callback&scope=openid
```

This will prompt you to perform authentication, and it will return a code. 
Use that code in the following request to get an access token, remember to put in the code and client secret.

``` SHELL
curl -X POST \
  https://login.microsoftonline.com/<tenantname>.onmicrosoft.com/oauth2/v2.0/token \
  -H 'Accept: */*' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Host: login.microsoftonline.com' \
  -H 'accept-encoding: gzip, deflate' \
  -H 'cache-control: no-cache' \
  -d 'redirect_uri=https%3A%2F%2F<yourpythonfunction>.azurewebsites.net%2Fcallback&client_id=<appid>&grant_type=authorization_code&code=<put code here>&client_secret=<put client secret here>&scope=https%3A%2F%2Fmytestapp.<tenantname>.onmicrosoft.com%2Fuser_impersonation'
  ```
 
 3. Once you get the access token, make a GET request to `https://<yourpythonfunction>.azurewebsites.net/api/user` with the access token as a Authorization Bearer header. Verify that you get an output similar to the below. The values marked as ..removed.. will have actual values in your output.

``` JSON
{
    "aud": "https://funcapi.<tenantname>.onmicrosoft.com",
    "iss": "https://sts.windows.net/<tenantid>/",
    "iat": 1571732525,
    "nbf": 1571732525,
    "exp": 1571736425,
    "acr": "1",
    "aio": "..removed..",
    "amr": [
        "pwd"
    ],
    "appid": "..removed..",
    "appidacr": "1",
    "email": "..removed..",
    "family_name": "..removed..",
    "given_name": "..removed..",
    "idp": "..removed..",
    "ipaddr": "..removed..",
    "name": "..removed..",
    "oid": "..removed..",
    "scp": "user_impersonation",
    "sub": "..removed..",
    "tid": "..removed..",
    "unique_name": "..removed..",
    "uti": "..removed..",
    "ver": "1.0"
}
```



## Build API in Docker

### Build and run the API

* Run [build.sh](build.sh) to build the Docker image

* Run [run.sh](run.sh) to run the image, the server is visible at http://localhost:5000. Use the /data secure endpoint to retrieve data


## Build and deploy the Power BI connector

* Build the pbi-connector project in Visual Studio and use F5 debugging to test it within VS

* [Deploy the PBI custom connector .mez file](https://github.com/microsoft/DataConnectors/blob/master/docs/m-extensions.md#build-and-deploy-from-visual-studio)

* [Configure and run the connector](https://github.com/microsoft/DataConnectors)