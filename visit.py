from datetime import datetime

from model import Flight, Location


async def get_all_paths(
    adjacency_matrix: dict[Location, list[Location]], source: Location,
    destination: Location
) -> list[list[Location]]:
    visited_list: list[list[Location]] = []
    _get_paths(adjacency_matrix, source, destination, [], visited_list)
    return visited_list


def _get_paths(
    graph: dict[Location, list[Location]],
    current_vertex: Location,
    destination: Location,
    visited: list[Location],
    path: list[list[Location]],
):
    visited.append(current_vertex)
    if current_vertex == destination:
        path.append(visited)
    else:
        for vertex in graph[current_vertex]:
            if vertex not in visited:
                _get_paths(graph, vertex, destination, visited.copy(), path)


async def get_best_flight(
    flights: list[Flight],
    origin: Location,
    destination: Location,
    after: datetime | None = None,
    before: datetime | None = None,
) -> Flight | None:
    best = None
    for flight in flights:
        if flight.origin != origin or flight.destination != destination:
            continue
        if after is None:
            if before is None:
                if best is None or best.price > flight.price:
                    best = flight
            elif flight.date < before:
                if best is None or best.price > flight.price:
                    best = flight
        elif flight.date >= after:
            if before is None:
                if best is None or best.price > flight.price:
                    best = flight
            elif flight.date < before:
                if best is None or best.price > flight.price:
                    best = flight
    return best
