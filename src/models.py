from sqlalchemy.orm import mapped_column, Mapped

from src.database import intpk, str_256, created_at, updated_at, Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[bytes] = mapped_column(nullable=False)
    first_name: Mapped[str_256]
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=True)
    is_stuff: Mapped[bool] = mapped_column(default=False, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
