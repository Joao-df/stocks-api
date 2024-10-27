from sqlalchemy.orm import Mapped, mapped_column

from app.models.tables.base import Base


class Purchases(Base):
    __tablename__: str = "purchases"

    company_code: Mapped[str] = mapped_column()
    amount: Mapped[int] = mapped_column()
