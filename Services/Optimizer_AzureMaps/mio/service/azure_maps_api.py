from datetime import datetime
import aiohttp
import json
import logging

origins_list = []

class AzureMapsApi:
    def __init__(self, api_key) -> None:
        self.travel_mode = "car"
        self.start_time = datetime.now().isoformat()
        self.time_unit = "second"
        if api_key is None:
            raise ValueError("Error: No api key provided")
        self.api_key = api_key

    async def route_matrix(self, origins, travel_mode=None, start_time=None, time_unit=None):
        origins_list = []
        travel_mode = travel_mode or self.travel_mode
        start_time = start_time or self.start_time
        time_unit = time_unit or self.time_unit
        url = f"https://atlas.microsoft.com/route/matrix/sync/json?api-version=1.0"\
            f"&subscription-key={self.api_key}"\
            f"&travelMode={travel_mode}"
        
        logging.info("URL - "+url)
        origins_split = origins.split(';')
        for index,value in enumerate(origins_split):
            value_split = value.split(',')
            origin = []
            origin.append(float(value_split[1]))
            origin.append(float(value_split[0]))
            origins_list.append(origin)

        inner_body = {
            "type" : "MultiPoint",
            "coordinates": origins_list,
        }
        input_body = {
            "origins": inner_body,
            "destinations": inner_body
        }
        jsonBody = json.dumps(input_body)
        reqHeaders = {'content-type': 'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=jsonBody, headers=reqHeaders) as rsp:
                result = await rsp.json()
        return result