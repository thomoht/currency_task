import requests
import json

API_URL = "http://api.nbp.pl/api/exchangerates/rates/a/{currency}/?format=json"
TIMEOUT = 10

class NbpExchangeRates:
    def _get(self, currency: str) -> dict:
        url = API_URL.format(currency=currency)
        response = requests.get(url.format(currency=currency), timeout=TIMEOUT)
        if response.status_code != 200:
            raise ConnectionError()
        return json.loads(response.text)
    
    def _prepere_data(self, data: dict) -> dict:
        return {
            "date": data['rates'][0]['effectiveDate'],
            "rate": data['rates'][0]['mid']
        }
    
    def get_rate(self, currency: str) -> dict:
        raw_data = self._get(currency)
        return self._prepere_data(raw_data)
    