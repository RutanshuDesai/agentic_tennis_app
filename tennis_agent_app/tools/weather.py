import requests
DEFAULT_BASE_URL="https://api.worldweatheronline.com/premium/v1/weather.ashx"

class WorldWeatherClient():
    """
    Initialize weather api client. This class is used to get the weather data. 
    """

    def __init__(
    self,
    api_key: str,
    base_url: str = DEFAULT_BASE_URL,
    timeout: int = 10,
    ) -> None:

        '''
        Docstring for __init__
        
        Params
        --------
        api_key: Get the key from world weather to access the data. 
        base_url: Default URL is provided. If needs a change then enter it. 
        '''

        self.api_key=api_key
        self.base_url=base_url
        self.timeout=timeout

    def get_weather(self, city: str, date: str | None=None) -> dict:
        '''
        Get weather data for a city and for a specfic date. If not date provided, uses today's date. Requires City string value. 
        
        Params
        ---------
        city: name of the city looking for weather
        data: optional - look for a specfic date. If not date provided, default is today's date set by the API. 

        Returns response from the API
        '''

        params = {
            "key": self.api_key,
            "q": city,
            "format": "json",
            "num_of_days": 1,
            "tp": 1,           # hourly data
            "units": "us"      # Fahrenheit, mph
        }

        if date:
            params["date"] = date  # YYYY-MM-DD

        response = requests.get(self.base_url, timeout=self.timeout, params=params)
        response.raise_for_status()

        return response.json()
    
class TennisWeatherService:
    def __init__(self, weather_client: WorldWeatherClient):
        '''
        Constructor to get in the weather client
        
        Parameter
        -------
        weather_client: WorldWeatherClient 
        '''
        self.weather_client=weather_client


    def get_hourly_play_conditions(
        self,
        city: str,hour: int,
        date:str | None = None
        ) -> dict:
        """Return weather info for a specific hour.

        Assumes `raw_data["data"]["weather"][0]["hourly"]` contains 24 hourly buckets
        (tp=1) ordered from 00:00 → 23:00.

        Params
        ---------
        city: city of weather interest
        date: specify a date of interest format YYYY-MM-DD else None value. None means, the API will give weather for today's date. 
        hour: 0–23 (24-hour format)

        Returns
        ---------
        A dictionary with temp F, wind mph, rain prob pct and time of the weather

        """
        if not (0 <= hour <= 23):
            raise ValueError("hour must be between 0 and 23")


        raw_data=self.weather_client.get_weather(city, date)
        hourly_data = raw_data["data"]["weather"][0]["hourly"]

        # simplest: hour 0 maps to index 0, hour 23 maps to index 23
        h = hourly_data[hour]

        # WWO time format: "0", "100", ..., "2300" (strings)
        expected_time = str(hour * 100)
        if str(h.get("time")) != expected_time:
            raise KeyError(f"Expected time={expected_time} at index={hour}, got time={h.get('time')}")

        actual_time = f"{int(h['time']):04d}"  # e.g. "1300"
        fetched_time_str = f"{int(actual_time[:2]):02d}:{int(actual_time[2:]):02d}"

        return {
            "temperature_f": float(h["tempF"]),
            "wind_mph": float(h["windspeedMiles"]),
            "rain_probability_pct": float(h.get("chanceofrain", 0)),
            "fetched_date": raw_data['data']['weather'][0]['date'],
            "fetched_time": fetched_time_str,
        }
