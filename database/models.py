from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Text, BigInteger, DateTime, func, ForeignKey

class Base(DeclarativeBase):
    created:Mapped[DateTime]=mapped_column(DateTime,default=func.now())
    updated:Mapped[DateTime]=mapped_column(DateTime,default=func.now(),onupdate=func.now())

class User(Base):
    __tablename__='users'
    tg_id=mapped_column(BigInteger)
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)

class Cart(Base):
    __tablename__='carts'
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    body:Mapped[str]=mapped_column(Text)
    user:Mapped[int]=mapped_column(ForeignKey('users.id'))

class Category(Base):
    __tablename__='categories'
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    title:Mapped[str]=mapped_column(String(20),nullable=False)
    belong:Mapped[str]=mapped_column(String(20),nullable=False)
    image:Mapped[str]=mapped_column(String(150))
    
class Item(Base):
    __tablename__='items'
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str]=mapped_column(String(30),nullable=False)
    details:Mapped[str]=mapped_column(Text)
    price:Mapped[float]=mapped_column(Float(asdecimal=True),nullable=False)
    image:Mapped[str]=mapped_column(String(150))
    category:Mapped[int]=mapped_column(ForeignKey('categories.id'))
    
class Dest(Base):
    __tablename__='dests'
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    country:Mapped[str]=mapped_column(String(30),nullable=False)
    town:Mapped[str]=mapped_column(String(30),nullable=False)
    street:Mapped[str]=mapped_column(String(30),nullable=False)
    house:Mapped[str]=mapped_column(String(10),nullable=False)
    room:Mapped[str]=mapped_column(String(5))
    user:Mapped[int]=mapped_column(ForeignKey('users.id'))
    
class Cafe(Base):
    __tablename__='cafes'
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    country:Mapped[str]=mapped_column(String(30),nullable=False)
    town:Mapped[str]=mapped_column(String(30),nullable=False)
    street:Mapped[str]=mapped_column(String(30),nullable=False)
    house:Mapped[str]=mapped_column(String(10),nullable=False)
    
class Phone(Base):
    __tablename__='phones'
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    number:Mapped[str]=mapped_column(String(20),nullable=False)
    user:Mapped[int]=mapped_column(ForeignKey('users.id'))
    
class Order(Base):
    __tablename__='orders'
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    cart:Mapped[str]=mapped_column(Text)
    delivery:Mapped[str]=mapped_column(String(20))
    dest:Mapped[str]=mapped_column(Text)
    cafe:Mapped[str]=mapped_column(Text)
    phone:Mapped[str]=mapped_column(String(25))
    user:Mapped[int]=mapped_column(ForeignKey('users.id'))
    
class Locale(Base):
    __tablename__='locales'
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    country:Mapped[str]=mapped_column(String(30))
    town:Mapped[str]=mapped_column(String(30))