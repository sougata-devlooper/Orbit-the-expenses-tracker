from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base
import enum

class CategoryEnum(str, enum.Enum):
    Need = "Need"
    Want = "Want"
    Invest = "Invest"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    expenses = relationship("Expense", back_populates="owner")
    limits = relationship("Limit", back_populates="owner")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    category = Column(SQLEnum(CategoryEnum), nullable=False)
    note = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="expenses")

class Limit(Base):
    __tablename__ = "limits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    monthly_limit = Column(Float, nullable=False)

    owner = relationship("User", back_populates="limits")
