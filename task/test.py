import os
import json
import unittest
from .currency_converter import PriceCurrencyConverterToPLN, ConvertedPricePLN
from .connectors.database import JsonFileDatabaseConnector, SqliteDatabaseConnector
from .connectors.local import FileExchangeRates
from .connectors.nbp import NbpExchangeRates
from datetime import date, timedelta

TEST_RATE_DATE = "2023-10-01"
TEST_RATE = 4.10

FILE_RATES_SOURCE = "currency_rates_unittest.json"
DATABASE_FILE = "unittest_database.json"
DATABASE_SQLITE = "unittest_database.sqlite3"

TEST_PRICE_OBJECT = ConvertedPricePLN(1, "PLN", 1, TEST_RATE_DATE, 1)

class TestRateEngine:
    def get_rate(self, currency: str) -> dict:
        return {
            "date": TEST_RATE_DATE,
            "rate": TEST_RATE
        }

class TestConverterMethods(unittest.TestCase):
    def test_converter(self):
        converter = PriceCurrencyConverterToPLN()
        result = converter.convert_to_pln(TestRateEngine(), price=1.0001, currency="USD")
        self.assertEqual(result.price_in_source_currency, 1.0)
        self.assertEqual(result.currency, "USD")
        self.assertEqual(result.currency_rate, TEST_RATE)
        self.assertEqual(result.currency_rate_fetch_date, TEST_RATE_DATE)
        self.assertEqual(result.price_in_pln, 4.10)
    
class TestSourceFile(unittest.TestCase):
    def setUp(self):
        self.source_data = {"USD": [{"date": "2020-01-01", "rate": 1}, {"date": TEST_RATE_DATE, "rate": TEST_RATE}, {"date": "2350-01-01", "rate": 1}]}
        with open(FILE_RATES_SOURCE, "w") as file:
            json.dump(self.source_data, file)
        self.source = FileExchangeRates(FILE_RATES_SOURCE)

    def test_data(self):
        self.assertEqual(self.source._data, self.source_data)

    def test_get_rate(self):
        result = self.source.get_rate("usd")
        self.assertEqual(result['date'], TEST_RATE_DATE)
        self.assertEqual(result['rate'], TEST_RATE)
    
    def test_unexpected_currency(self):
        with self.assertRaises(IndexError):
            self.source.get_rate("xxx")
            
    def addCleanup(self, ):
            print("asdasd")
    
class TestSourceNBP(unittest.TestCase):
    def setUp(self):
        self.source = NbpExchangeRates()
        
    def test_nbp_date(self):
        result = self.source.get_rate("usd")
        expected_date = date.today()
        if expected_date.weekday()>=5:
            expected_date = expected_date - timedelta(days=expected_date.weekday()-4)
        self.assertEqual(date.fromisoformat(result['date']), expected_date)
        
    def test_nbp_unexpected_currency(self):
        with self.assertRaises(ConnectionError):
            self.source.get_rate("xxx")
    
class TestDatabaseFile(unittest.TestCase):
    def setUp(self):
        self.db = JsonFileDatabaseConnector(DATABASE_FILE)
        
    def test1_empty_db(self):
        result = self.db.get_all()
        self.assertEqual(len(result), 0)
    
    def test2_first_save(self):
        inserted_id = self.db.save(TEST_PRICE_OBJECT)
        self.assertEqual(inserted_id, 1)
        
    def test3_first_element(self):
        result = self.db.get_all()
        self.assertEqual(len(result), 1)
        converted_price = self.db.get_by_id(1)
        self.assertEqual(converted_price, TEST_PRICE_OBJECT)
        
    def test4_second_save(self):
        inserted_id = self.db.save(TEST_PRICE_OBJECT)
        self.assertEqual(inserted_id, 2)
        
    def test5_second_element(self):
        result = self.db.get_all()
        self.assertEqual(len(result), 2)
        converted_price = self.db.get_by_id(2)
        self.assertEqual(converted_price, TEST_PRICE_OBJECT)

class TestDatabaseSQLite(TestDatabaseFile):
    def setUp(self):
        self.db = SqliteDatabaseConnector(DATABASE_SQLITE)
        
    def tearDown(self):
        self.db.close()

def clean():
    if os.path.exists(FILE_RATES_SOURCE):
        os.remove(FILE_RATES_SOURCE)
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
    if os.path.exists(DATABASE_SQLITE):
        os.remove(DATABASE_SQLITE)
    

if __name__ == '__main__':
    clean()
    unittest.main(verbosity=1, exit=False)
    clean()