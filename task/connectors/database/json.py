import functools
import json
from ...config import JSON_DATABASE_NAME
from ...currency_converter import ConvertedPricePLN


class JsonFileDatabaseConnector:
    def __init__(self, database:str | None=None) -> None:
        self._database_name = database if database else JSON_DATABASE_NAME
        self._data = self._read_data()

    def _read_data(self) -> dict:
        try:
            with open(self._database_name, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

        
    def _save_data(self):
        with open(self._database_name, "w") as file:
            return json.dump(self._data, file)
        
    @property
    def _get_next_id(self) -> int:
        if not self._data:
            return 1
        max_id_in_db = int(functools.reduce(lambda first, last: first if int(first) > int(last) else last, self._data))
        return max_id_in_db + 1
    
    def _prepare_response(self, data: dict) -> ConvertedPricePLN:
        def __calc_original_price(pln_price: float, rate: float) -> float:
            # missing in database, can be deleted if database store original price
            return round(pln_price / rate  ,2)
        return ConvertedPricePLN(
                        __calc_original_price(data['price_in_pln'], data['rate']),
                        data['currency'],
                        data['rate'],
                        data['date'],
                        data['price_in_pln'])
    
    def save(self, entity: ConvertedPricePLN) -> int:
        entity_id = self._get_next_id
        self._data[str(entity_id)] = {
            "id": entity_id,
            "currency": entity.currency,
            "rate": entity.currency_rate,
            "price_in_pln": entity.price_in_pln,
            "date": entity.currency_rate_fetch_date
        }
        self._save_data()
        return entity_id

    def get_all(self) -> list[ConvertedPricePLN]:
        return list(map(self._prepare_response, self._data.values()))

    def get_by_id(self, pk: int) -> ConvertedPricePLN | None:
        try:
            raw_data = self._data[str(pk)]
            return self._prepare_response(raw_data)
        except KeyError:
            return None
        

