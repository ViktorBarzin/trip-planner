import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import flight_loader
import visit
from model import Flight, Location, Trip


async def generate_trip(
    *,
    flights: list[Flight],
    origin: Location,
    destination: Location,
    must_visit: list[Location],
    duration_per_location: dict[Location, timedelta],
) -> Trip:
    """
    1. find all routes from origin to destination visiting must_visit
    2. for each route, find the best price for each trip
    3. sort trips by lowest price
    """

    # TODO(viktorbarzin): currently doing greedy i.e pick first available flight

    # build location adjacency matrix
    location_matrix: dict[Location, list[Location]] = defaultdict(list)
    for flight in flights:
        if flight.destination not in location_matrix[flight.origin]:
            location_matrix[flight.origin].append(flight.destination)

    # get all paths between the two locations
    paths: list[list[Location]] = await visit.get_all_paths(
        location_matrix, origin, destination
    )

    # leave only paths that include all must visit locations
    paths = [path for path in paths if set(must_visit).issubset(set(path))]

    trips: list[Trip] = []
    for path in paths:
        route: list[Flight] = []
        for idx in range(len(path) - 1):
            if len(route) == 0:
                after = None
            else:
                after = route[-1].date + duration_per_location.get(
                    route[-1].destination, timedelta(hours=24)
                )
            flight = await visit.get_best_flight(
                flights,
                path[idx],
                path[idx + 1],
                after=after,
                before=datetime(day=18, month=12, year=2022)
            )
            if flight is None:
                break
            route.append(flight)
        trip = Trip(flights=route)
        print(trip)
        trips.append(trip)

    trips.sort(key=lambda x: x.price)

    # Cheapest trip
    return trips[0]


async def get_flights() -> list[Flight]:
    paths = [
        # London
        'flights/lon-mle-12-2022.png',
        'flights/lon-hkt-12-2022.png',
        'flights/lon-bkk-12-2022.png',
        # Male
        'flights/mle-hkt-12-2022.png',
        'flights/mle-bkk-12-2022.png',
        'flights/mle-otp-12-2022.png',
        'flights/mle-sof-12-2022.png',
        'flights/mle-dxb-12-2022.png',
        # Bangkok
        'flights/bkk-hkt-12-2022.png',
        'flights/bkk-mle-12-2022.png',
        'flights/bkk-sof-12-2022.png',
        'flights/bkk-otp-12-2022.png',
        'flights/bkk-dxb-12-2022.png',
        # Phuket
        'flights/hkt-bkk-12-2022.png',
        'flights/hkt-mle-12-2022.png',
        'flights/hkt-sof-12-2022.png',
        'flights/hkt-otp-12-2022.png',
        'flights/hkt-dxb-12-2022.png',
        # Dubai
        'flights/dxb-sof-12-2022.png',
        'flights/dxb-otp-12-2022.png',
    ]
    flights: list[Flight] = []
    for p in paths:
        flights.extend(await flight_loader.img_to_flights(Path(p)))
    return flights


async def main() -> None:
    flights: list[Flight] = await get_flights()
    await flight_loader.flights_to_csv(flights, Path('flights/flights.csv'))
    origin = Location.LON
    destination = Location.SOF
    must_visit = [Location.MLE, Location.HKT, Location.BKK]
    # TODO(viktorbarzin): ad minimum stay per location if needed
    duration_per_location = {}
    trip: Trip = await generate_trip(
        flights=flights,
        origin=origin,
        destination=destination,
        must_visit=must_visit,
        duration_per_location=duration_per_location
    )
    print(f'Cheapest route: {trip}\nFlight price: {trip.price}')


if __name__ == '__main__':
    asyncio.run(main())
