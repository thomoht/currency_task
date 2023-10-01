from sqlalchemy import create_engine, inspect
from sqlalchemy import String
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session
from ...config import SQLITE_DATABASE_NAME
from ...currency_converter import ConvertedPricePLN

class Base(DeclarativeBase):
    pass

class CurrencyConverted(Base):
    __tablename__ = "currency_converted"

    id: Mapped[int] = mapped_column(primary_key=True)
    currency: Mapped[str] = mapped_column(String(3))
    rate: Mapped[float]
    price_in_pln: Mapped[float]
    date: Mapped[str] = mapped_column(String(10))



class SqliteDatabaseConnector:
    def __init__(self, database:str | None=None) -> None:
        database_name = database if database else SQLITE_DATABASE_NAME
        self.engine = create_engine("sqlite:///{}".format(database_name))
        if not inspect(self.engine).has_table("currency_converted"):
            Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        
    def close(self):
        self.session.close()
        self.engine.dispose()
    
        
    def _prepare_response(self, data: CurrencyConverted) -> ConvertedPricePLN:
        def __calc_original_price(pln_price: float, rate: float) -> float:
            # missing in database, can be deleted if database store original price
            return round(pln_price / rate  ,2)
        return ConvertedPricePLN(
                        __calc_original_price(data.price_in_pln, data.rate),
                        data.currency,
                        data.rate,
                        data.date,
                        data.price_in_pln)

    def save(self, entity: ConvertedPricePLN) -> int:
        currency = CurrencyConverted(
            currency=entity.currency,
            rate=entity.currency_rate,
            price_in_pln=entity.price_in_pln,
            date=entity.currency_rate_fetch_date
        )
        self.session.add(currency)
        self.session.commit()
        return currency.id

    def get_all(self) -> list[ConvertedPricePLN]:
        query = select(CurrencyConverted)
        rows = self.session.scalars(query)
        return list(map(self._prepare_response, rows))

    def get_by_id(self, pk: int) -> ConvertedPricePLN:
        query = select(CurrencyConverted).where(CurrencyConverted.id==pk)
        raw_data = self.session.scalars(query).one()
        return self._prepare_response(raw_data)