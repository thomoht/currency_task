import functools
import json
from datetime import date


class FileExchangeRates:
    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._data = self._read_data()
        
    def _read_data(self) -> dict:
        with open(self._filename, "r") as file:
            return json.load(file)
    
    def _get(self, currency: str) -> dict:
        def find_closest_date(first: dict, second: dict) -> dict:
            first_date = date.fromisoformat(first['date'])
            second_date = date.fromisoformat(second['date'])
            if first_date > date.today():
                return second
            if second_date > date.today():
                return first
            return first if first_date > second_date else second
        if currency not in self._data:
            raise IndexError("currency not found in file source")
        return functools.reduce(find_closest_date, self._data[currency])
        
    def get_rate(self, currency: str) -> dict:
        return self._get(currency.upper())
    