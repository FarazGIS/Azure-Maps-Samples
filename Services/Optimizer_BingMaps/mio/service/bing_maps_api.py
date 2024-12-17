from datetime import datetime
import aiohttp

class BingMapsApi:
    def __init__(self, api_key) -> None:
        self.travel_mode = "driving"
        self.start_time = datetime.now().isoformat()
        self.time_unit = "second"
        if api_key is None:
            raise ValueError("Error: No api key provided")
        self.api_key = api_key

    async def distance_matrix(self, origins, travel_mode=None, start_time=None, time_unit=None):
        travel_mode = travel_mode or self.travel_mode
        start_time = start_time or self.start_time
        time_unit = time_unit or self.time_unit
        url = f"https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix"\
              f"?origins={origins}"\
              f"&destinations={origins}"\
              f"&travelMode={travel_mode}"\
              f"&startTime={start_time}"\
              f"&timeUnit={time_unit}"\
              f"&key={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as rsp:
                result = await rsp.json()
        return result