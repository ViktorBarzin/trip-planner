import enum
from dataclasses import dataclass
from datetime import datetime


class Location(enum.Enum):
    LON = 'London'
    AUH = 'Abu Dhabi'
    MLE = 'Male/Maldives'
    SOF = 'Sofia'
    TSR = 'Timisoara'
    HKT = 'Phuket'
    BKK = 'Bangkok'
    OTP = 'Bucharest'
    DXB = 'Dubai'


@dataclass
class Flight:
    date: datetime
    origin: Location
    destination: Location
    price: float


@dataclass
class Trip:
    flights: list[Flight]

    @property
    def price(self) -> float:
        return sum([flight.price for flight in self.flights])
