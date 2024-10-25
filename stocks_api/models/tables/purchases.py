from sqlalchemy.orm import Mapped, mapped_column

from stocks_api.models.tables.base import Base


class Purchases(Base):
    __tablename__: str = "purchases"

    company_code: Mapped[str] = mapped_column()
    amount: Mapped[str] = mapped_column()
