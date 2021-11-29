from itertools import cycle

from model_bakery.recipe import Recipe

from .models import Address


countries = ["Russia", "Italy", "Germany", "France", "USA"]
cities = [
    "Moscow",
    "Saint Petersburg",
    "Rome",
    "Milan",
    "Berlin",
    "Munich",
    "Paris",
    "Marseille",
    "New York",
    "Chicago",
]
streets = [
    "Tverskaya Ulitsa, 12",
    "Bolshaya Nikitskaya Ulitsa, 24",
    "Nikolskaya Ulitsa, 38",
    "Via Cavour, 17",
    "Via della Conciliazione, 28",
    "Via del Corso, 4",
    "Rosa-Luxemburg-Straße, 8",
    "Mohrenstraße, 47",
    "Frankfurter Allee, 56",
    "Avenue Victor Hugo, 87",
    "Rue de Rivoli, 21",
    "Rue Montorgueil, 13",
    "Manhattan Avenue (Brooklyn), 26",
    "Atlantic Avenue (New York City), 19",
    "Fort Washington Avenue, 7",
]

address = Recipe(
    _model=Address,
    country=cycle(countries),
    city=cycle(cities),
    street=cycle(streets),
)
