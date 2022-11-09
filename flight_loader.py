from datetime import datetime
from pathlib import Path

import aiofiles
import numpy as np
import pytesseract
from PIL import Image

from model import Flight, Location


async def load_flights(file_path: Path) -> list[Flight]:
    async with aiofiles.open(file_path, 'r') as f:
        lines = await f.readlines()

    flights: list[Flight] = []
    for line in lines:
        flights.append(await _flight_from_csv(line))
    return flights


async def _flight_from_csv(line: str) -> Flight:
    """
    assume line format:
    origin,destination,date,price 
    """
    origin, destination, date_str, price = line.split(',')
    return Flight(
        origin=Location[origin],
        destination=Location[destination],
        date=_date_from_str(date_str),
        price=float(price)
    )


def _date_from_str(date: str) -> datetime:
    return datetime.strptime(date, '%Y-%m-%d')


async def img_to_flights(img: Path) -> list[Flight]:
    """
    img format "origin-destination-month-year.png" 

    1. Read img
    2. Get prices
    3. Build map[datetime, price]
    4. Dump file to csv
    """
    # Get origin and destination airports based on img name
    if len(str(img).split('-')) != 4:
        raise ValueError(
            'Expected img path name to be in the '
            f'format "origin-destination-month-year.png". Got {img}'
        )
    # Parse file name
    _origin, _dest, _month, _year = img.stem.split('-')
    origin: Location = Location[_origin.upper()]
    destination: Location = Location[_dest.upper()]
    month: int = int(_month)
    year: int = int(_year)

    # Parse prices
    img = np.array(Image.open(str(img)))
    img_strings: list[str] = pytesseract.image_to_string(
        img, config='--psm 11'
    ).split('\n')
    prices: list[int] = [
        int(val[1:].replace(',', '')) for val in img_strings if '£' in val
    ]

    flights: list[Flight] = []

    # Create flights list
    for idx, price in enumerate(prices):
        flight = Flight(
            date=datetime(year, month, idx + 1),
            origin=origin,
            destination=destination,
            price=price
        )
        flights.append(flight)

    return flights


async def flights_to_csv(flights: list[Flight], path: Path) -> None:
    serialized = [
        f'{f.origin.name},{f.destination.name},{f.date.strftime("%Y-%m-%d")},{f.price}'
        for f in flights
    ]
    async with aiofiles.open(path, 'w') as f:
        await f.write("\n".join(serialized))
