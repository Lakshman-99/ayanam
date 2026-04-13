"""
KP Significator Calculator

Implements KSK 4-fold (original Krishnamurti) significator method.
KSK 6-fold and Khullar methods will be added in Phase 2.

In KP, a planet significates a house if:
  Priority 1: Planet is in the star (nakshatra) of a planet OCCUPYING that house
  Priority 2: Planet occupies that house
  Priority 3: Planet is in the star of the lord (sign ruler) of that house cusp
  Priority 4: Planet is the lord (sign ruler) of that house cusp

The house with the strongest connection = lowest priority number.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.engine.planets import PlanetData
from app.engine.houses import HouseSystemData


@dataclass
class SignificatorData:
    """Significator analysis result for a single planet."""

    planet: str
    houses_signified: list[int] = field(default_factory=list)
    # How it signifies each house: "star_of_occupant", "occupant", "star_of_lord", "lord"
    methods: dict[int, str] = field(default_factory=dict)


def calculate_significators_ksk4(
    planets: dict[str, PlanetData],
    houses: HouseSystemData,
) -> dict[str, SignificatorData]:
    """
    KSK 4-fold significator calculation.

    Returns dict keyed by planet name, each containing the list of houses
    that planet signifies and the method by which it does so.
    """
    # Build house→occupants mapping
    house_occupants: dict[int, list[str]] = {i: [] for i in range(1, 13)}
    for p_name, p_data in planets.items():
        if p_data.house > 0:
            house_occupants[p_data.house].append(p_name)

    # Build house→cusp_lord mapping
    house_lord: dict[int, str] = {}
    for cusp in houses.cusps:
        house_lord[cusp.house] = cusp.sign_lord

    # Build planet→nakshatra_lord mapping
    planet_star_lord: dict[str, str] = {
        p_name: p_data.star_lord for p_name, p_data in planets.items()
    }

    result: dict[str, SignificatorData] = {
        p_name: SignificatorData(planet=p_name) for p_name in planets
    }

    for house_num in range(1, 13):
        occupants = house_occupants[house_num]
        lord = house_lord[house_num]

        for p_name, p_data in planets.items():
            sig = result[p_name]

            # Priority 1: planet is in the star of an occupant of this house
            if planet_star_lord[p_name] in occupants and house_num not in sig.houses_signified:
                sig.houses_signified.append(house_num)
                sig.methods[house_num] = "star_of_occupant"
                continue

            # Priority 2: planet occupies this house
            if p_data.house == house_num and house_num not in sig.houses_signified:
                sig.houses_signified.append(house_num)
                sig.methods[house_num] = "occupant"
                continue

            # Priority 3: planet is in the star of the lord of this house cusp
            if planet_star_lord[p_name] == lord and house_num not in sig.houses_signified:
                sig.houses_signified.append(house_num)
                sig.methods[house_num] = "star_of_lord"
                continue

            # Priority 4: planet is the lord of this house cusp
            if p_name == lord and house_num not in sig.houses_signified:
                sig.houses_signified.append(house_num)
                sig.methods[house_num] = "lord"

    # Sort each planet's signified houses by number
    for sig in result.values():
        sig.houses_signified.sort()

    return result


def get_house_significators(
    significators: dict[str, SignificatorData],
    house_num: int,
) -> list[tuple[str, str]]:
    """
    Return list of (planet_name, method) for all planets signifying the given house,
    sorted by KSK priority (star_of_occupant first, lord last).
    """
    priority = {"star_of_occupant": 1, "occupant": 2, "star_of_lord": 3, "lord": 4}

    results = []
    for p_name, sig in significators.items():
        if house_num in sig.houses_signified:
            method = sig.methods[house_num]
            results.append((p_name, method))

    results.sort(key=lambda x: priority.get(x[1], 99))
    return results
