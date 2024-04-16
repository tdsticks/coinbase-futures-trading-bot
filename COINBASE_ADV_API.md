### Coinbase Advanced API

You've need API keys from the Advanced API - not the original Coinbase API
 https://www.coinbase.com/cloud/products/advanced-trade-api

1. Create a new API, give it a name and select your portfolio (default if you have only one)
2. Check the Permissions for View and Trade only.
3. You can restrict the IP if you know it for your local and host server for extra security.
4. Add the API_KEY and API_SECRET to the .env file (after you've copied from .env.example)
5. To get your UUID, either grab from the newly created API in the Coinbase Advanced API 
   UI when you click on it (Key ID) or from the tail end of the API_KEY (after the last slash)
   it should be able 36 characters long.