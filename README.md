# How to get started
Itinerary optimization is a two-step process that requires a travel cost matrix and an optimization engine to find the best outcome. A cost matrix represents the cost of traveling between every two set of locations in the problem. It can be calculated using the Bing Maps Distance Matrix or Azure Maps Route Matrix service.

When requesting the cost matrix, it is necessary to pass all the waypoints as origins and destinations in the input to get travel times between all locations. The optimizer needs to know the cost to traverse between each node to generate the best outcome. For example, a restaurant has 2 drivers and needs to deliver food to 5 locations, you would need to input 7 waypoints as origin and 7 waypoints as destination assuming the both agents have different start locations. The matrix should look like the following:

|        | Agent1 | Agent2 | Stop1 | Stop2 | Stop3 | Stop4 | Stop5 |
|--------|--------|--------|-------|-------|-------|-------|-------|
| Agent1 | 0      | 2      | 5     | 1     | 3     | 1     | 2     |
| Agent2 | 4      | 0      | 5     | 6     | 1     | 7     | 3     |
| Stop1  | 1      | 2      | 0     | 7     | 8     | 5     | 1     |
| Stop2  | 4      | 6      | 5     | 0     | 4     | 1     | 1     |
| Stop3  | 2      | 2      | 2     | 1     | 0     | 1     | 2     |
| Stop4  | 1      | 1      | 1     | 4     | 4     | 0     | 3     |
| Stop5  | 3      | 8      | 5     | 6     | 2     | 1     | 0     |

# Prerequisites
Use of the following software and library is required:

- OR tools – The solution uses OR tools for the optimiser. The package can be installed from Install OR-Tools. The library used in the solution is OR Tools for Python. This guide is to help you get started with an open-source library. You could use any open-source solution of your choice that best suits your requirements.
- Distance Matrix – You can use Bing Maps Distance Matrix or Azure Maps Route Matrix based on your preference.
- Azure Tools Extension for VS Code – Can be downloaded from Azure Tools.
- Application Insights (optional) – To write logs and monitor your function app for debugging.
- Python 3.11
- Visual Studio Code

# Setup
1. Download the package you need.
   - Bing Maps Optimizer
   - Azure Maps Optimizer

2. Install all the required tools and packages. Refer to requirements.txt in the sample. You can run the following command to install the dependencies using the requirements.txt file. 
<br /><br />pip install-r requirement.txt
4. Open the project folder in VS Code and download the Azure Tools in VS Code
5. Create Azure function to build an API that returns the travel itinerary for the given set of agents and stops. The code sample implements the vehicle Routing problem for multiple drivers for the best optimal path.
6. In MIO.html, find the string “https://miodemo.azurewebsites.net” and replace “miodemo” with the Function App name. For example, if the app name is “optimize”, then the new string will be “https://optimize.azurewebsites.net”
7. Under the applications settings of the newly created Function app, add the following key-value pairs. To access App settings, login to Microsoft Azure portal >your function app > Settings > Environment variables.
   - For Bing Maps
     <br />BME_KEY = <Bing Maps Developer Key, get one for free on Bing Maps Dev Center>. This BME_KEY will be used to make requests to the Bing Maps Distance Matrix API.
   - Azure Maps
     <br />API_KEY = <Azure Maps Subscription Key> You will need to create an Azure Maps account to get the subscription key if you don’t have an account. This API_KEY will be used to make requests to the Azure Maps Route Matrix API. Additionally in MIO.html,        find the string "your-key" and replace it with the Azure Maps subscription key for the app authentication.
8. (Optional) This step is optional if you want to write logs of your Azure function for debugging. if you don't want to create it, you can modify the init_log() function under utils/log.py to comment the part about Azure Application Insights.
   <br /><br />MIO_APPINSIGHT_CONN_STRING=<Connection String of Application Insight, you need to create an Application Insights resource on Azure and get the connection string>
9. In VS Code, open the Azure workspace, select the Azure Functions option, and select Deploy to Function App to deploy your solution to Azure.

Note: The sample supports assigning stops to multiple agents delivering multiple stops, but you can add additional constraints such as capacity, pickups and deliveries and resource constraints to your solution. There are additional VRP examples added to this project that you can refer to. You can find more samples on the OR tools webpage.

# Usage
The code sample contains an html page that you can use to request the endpoint and visualize the results on a map. To see the results.
- Browse https://<your function app name>.azurewebsites.net/mioui for the sample html and use https://<your function app name>.azurewebsites.net/api/mio to access the endpoint.
- For Bing Maps.
   - In the sample application, enter your Bing Maps dev key.
   - Note: The sample uses Bing Maps base map data and Route service to get route for the agents.
- For Azure Maps, it will use the subscription key from the MIO.html file.
- In the app, enter the request body for the custom optimizer API which is the vehicle and location information in a GeoJson format. Refer to the examples in the sample code for template. For a quick start, the application is prepopulated with a sample request body.
- Click Get Routes.
- The results will be displayed on a table sorted by the agent vehicles and the order in which they will visit the stops. The routes will be drawn on the map and color coded to match the corresponding agent in the results table.
  
  ![image](https://github.com/user-attachments/assets/611602d1-fca2-4e3b-b9ec-0a6409f22f02)

