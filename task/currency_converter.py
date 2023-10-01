from dataclasses import dataclass


@dataclass(frozen=True)
class ConvertedPricePLN:
    price_in_source_currency: float
    currency: str
    currency_rate: float
    currency_rate_fetch_date: str
    price_in_pln: float


class PriceCurrencyConverterToPLN:
    def convert_to_pln(self, rates_engine, currency: str, price: float) -> ConvertedPricePLN:
        source_price = round(price, 2)
        rate_data = rates_engine.get_rate(currency)
        pln_price = round(source_price * rate_data['rate'], 2)
        return ConvertedPricePLN(source_price, currency, rate_data['rate'], rate_data['date'], pln_price)
