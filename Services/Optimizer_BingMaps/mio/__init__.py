import os
import logging
import json
import http.client
from pathlib import Path
from urllib.parse import unquote

import azure.functions as func
import aiofiles

from mio.service.bing_maps_api import BingMapsApi
from mio.service.optimizer import optimizer
from mio.utils.log import init_log

test_data = Path("examples/data/2_vehicles_3_waypoints.json").read_text()



async def mio(data: str) -> (int, str):
    try:
        data = json.loads(data)
    except (TypeError, ValueError) as ex:
        msg = f"Error: Invalid json:\n{ex}"
        logging.exception(msg)
        return http.client.BAD_REQUEST, msg
    except Exception as ex:
        msg = f"Error: Unhandled exception:\n{ex}"
        logging.exception(msg)
        return http.client.INTERNAL_SERVER_ERROR, msg

    try:
        # BME_KEY is the environment variable name for the Bing Maps API key which saved in Azure Function's Application Settings
        api = BingMapsApi(api_key=os.getenv("BME_KEY"))

        # Call Bing Maps API to get distance matrix, which is used as input for the optimizer
        # The distance matrix requires all points (start, end, waypoints) to be in one string
        vehicles = data.get("vehicles")
        vehicles_start = [vehicle["start"] for vehicle in vehicles]
        vehicles_end = [vehicle["end"] for vehicle in vehicles]
        waypoints = data.get("waypoints", None)
        waypoints_location = [w['location'] for w in waypoints]
        all_points_full_info = vehicles_start + vehicles_end + waypoints
        all_points = vehicles_start + vehicles_end + waypoints_location
        all_points_str = ";".join([f"{p[1]},{p[0]}" for p in all_points])

        bing_rsp = await api.distance_matrix(origins=all_points_str)

        distance_matrix = [[None] * len(all_points) for i in range(len(all_points))]
        if "statusCode" in bing_rsp and bing_rsp["statusCode"] == 200:
            # In this demo we only use the major route and skip the alternative routes
            # And we use the travelDuration as the distance/penalty between two points
            bing_distance_matrix = bing_rsp["resourceSets"][0]["resources"][0]["results"]
            for entry in bing_distance_matrix:
                distance_matrix[entry["originIndex"]][entry["destinationIndex"]] = entry["travelDuration"]
        else:
            raise ValueError(f"Error: Bing Maps API call failed:\n{bing_rsp}")

        # Call optimizer to get the optimized route
        input_body = {
            "distance_matrix" : distance_matrix,
            "num_vehicles": len(vehicles),
            "starts": [i for i in range(len(vehicles_start))],
            "ends": [i for i in range(len(vehicles_start), len(vehicles_start) + len(vehicles_end))]
        }
        optimizer_result = optimizer(input_body)

        output_response = []
        for vehicle_index, sequence in optimizer_result.items():
            output_item = {}
            vehicle = vehicles[vehicle_index]
            vehicle_id = vehicle["id"]
            output_item["id"] = vehicle_id
            output_item["locations"] = []
            for index in sequence:
                if index == sequence[0]:    # Start point
                    location = all_points_full_info[index]
                    output_item["locations"].append({"id": f"{vehicle_id}_start", "location": location})
                elif index == sequence[-1]: # End point
                    location = all_points_full_info[index]
                    output_item["locations"].append({"id": f"{vehicle_id}_end", "location": location})
                else:
                    location = all_points_full_info[index]
                    output_item["locations"].append(location)
            output_response.append(output_item)

        return http.client.OK, json.dumps(output_response)
    except Exception as ex:
        return http.client.INTERNAL_SERVER_ERROR, f"Error: Unhandled exception:\n{ex}"



async def main(req: func.HttpRequest) -> func.HttpResponse:
    init_log()
    route_path = req.route_params.get("route_path")
    logging.info(f"Request received: {req.url}, route_path: {route_path}")

    # This main function is used for both html and api requests entry point
    if route_path == "mioui":
        async with aiofiles.open("mio/mio.html", mode="r") as f:
            # mio.html will call api/mio after clicking "Get Route" button
            contents = await f.read()
            return func.HttpResponse(contents, mimetype="text/html")
    elif route_path == "api/mio":
        # Get GeoJSON either from query parameter "json" or from request body
        data = req.params.get("json")
        if data:
            data = unquote(data)
        else:
            try:
                data = req.get_body().decode("utf-8")
                if not data or len(data) == 0:
                    raise ValueError("No json data in request")
            except ValueError:
                logging.info("No json data in request, using test data")
                data = test_data
            except Exception as ex:
                return func.HttpResponse(f"Error: Unhandled exception:\n{ex}", status_code=http.client.INTERNAL_SERVER_ERROR)
        status_code, rsp = await mio(data)
        b = f'{{"status": {status_code}, "result": {rsp}}}'
        json_rsp = json.loads(f'{{"status": {status_code}, "result": {rsp}}}')
        return func.HttpResponse(json.dumps(json_rsp, indent=2), status_code=status_code)
    else:
        return func.HttpResponse(None, status_code=http.client.NOT_FOUND)