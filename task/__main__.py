import argparse
import sys
from logging import getLogger
from .currency_converter import PriceCurrencyConverterToPLN, ConvertedPricePLN
from .connectors.database import JsonFileDatabaseConnector, SqliteDatabaseConnector
from .connectors.local import FileExchangeRates
from .connectors.nbp import NbpExchangeRates
from .config import CURRENCY_CODES, DEFAULT_ENVIROMENT, DEFAULT_SOURCE, DEFAULT_SOURCE_FILE_RATES, SHOW_OUTPUT_INFO
logger = getLogger(__name__)

class Worker:
    def __init__(self) -> None:
        logger.debug("setup args parser")
        self._init_parser()
        logger.debug("parse inserted arguments")
        self.args = self.parser.parse_args()
        logger.debug("init PriceCurrencyConverterToPLN")
        self.converter = PriceCurrencyConverterToPLN()    
    
    def _init_parser(self) -> None:
        self.parser = argparse.ArgumentParser(description='Convert price in chosen currency to PLN')
        self.parser.add_argument('-e', '--env', help = "setup environment", choices=['dev', 'prod'], default=DEFAULT_ENVIROMENT)
        self.parser.add_argument('-s', '--source', help = "select source for currency converter", choices=['nbp', 'file'], default=DEFAULT_SOURCE)
        self.parser.add_argument('-f', '--filename', help = "filename for file currency converter", default=DEFAULT_SOURCE_FILE_RATES)

        self.parser.add_argument('price', help = "price in source currency", type=float)
        self.parser.add_argument('currency', help = "currency", choices=CURRENCY_CODES)
        
    def _setup_db(self) -> JsonFileDatabaseConnector | SqliteDatabaseConnector:
        return JsonFileDatabaseConnector() if self.args.env == 'dev' else SqliteDatabaseConnector()
    
    def _setup_source(self) -> FileExchangeRates | NbpExchangeRates:
        return FileExchangeRates(self.args.filename) if self.args.source == 'file' else NbpExchangeRates()
    
    def show_result_info(self, converted_price_pln: ConvertedPricePLN) -> None:
        print("{orginal_price} {currency} = {pln_price} PLN".format(
                orginal_price=converted_price_pln.price_in_source_currency,
                currency=converted_price_pln.currency,
                pln_price=converted_price_pln.price_in_pln
            ))
    
    def convertCurrency(self) -> float:
        logger.debug("setup database, env={}".format(self.args.env))
        db = self._setup_db()
        logger.debug("setup rates source, source={}".format(self.args.source))
        source = self._setup_source()
        logger.debug("convert price")
        converted_price_pln = self.converter.convert_to_pln(source, price=self.args.price, currency=self.args.currency)
        logger.debug("{}".format(converted_price_pln))
        logger.debug("save data to database")
        db.save(converted_price_pln)
        logger.debug("show output info is {}".format(SHOW_OUTPUT_INFO))
        if SHOW_OUTPUT_INFO:
            self.show_result_info(converted_price_pln)
        return converted_price_pln.price_in_pln
    
try:
    logger.info("Initiate job")
    w = Worker()
    logger.info("Converting currency")
    w.convertCurrency()
    logger.info("Job done!")
except Exception as err:
    logger.error(err, exc_info=True)
