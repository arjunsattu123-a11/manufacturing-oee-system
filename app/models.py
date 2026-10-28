
from sqlalchemy import Column, ForeignKey, Integer, String
from app.database import Base


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)


class Line(Base):
    __tablename__ = "lines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    line_id = Column(Integer, ForeignKey("lines.id"), nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    ideal_cycle_time_seconds = Column(Integer, nullable=False)

    
from sqlalchemy import DateTime, Float, Boolean, Text


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id = Column(String(50), primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    planned_quantity = Column(Integer, nullable=False)


class StateEvent(Base):
    __tablename__ = "state_events"

    id = Column(String(100), primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    state = Column(String(30), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


class ProductionCount(Base):
    __tablename__ = "production_counts"

    id = Column(String(100), primary_key=True)
    order_id = Column(String(50), ForeignKey("production_orders.id"), nullable=False)
    good_count = Column(Integer, nullable=False, default=0)
    scrap_count = Column(Integer, nullable=False, default=0)


class QualityInspection(Base):
    __tablename__ = "quality_inspections"

    id = Column(String(100), primary_key=True)
    order_id = Column(String(50), ForeignKey("production_orders.id"), nullable=False)
    inspected_quantity = Column(Integer, nullable=False)
    rejected_quantity = Column(Integer, nullable=False, default=0)


class DowntimeReason(Base):
    __tablename__ = "downtime_reasons"

    id = Column(Integer, primary_key=True)
    code = Column(String(30), unique=True, nullable=False)
    description = Column(String(200), nullable=False)


class OEEAggregate(Base):
    __tablename__ = "oee_aggregates"

    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    availability = Column(Float, nullable=False)
    performance = Column(Float, nullable=False)
    quality = Column(Float, nullable=False)
    oee = Column(Float, nullable=False)

