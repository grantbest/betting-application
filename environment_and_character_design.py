class AlienEnvironment:
    def __init__(self, climate, terrain, atmosphere):
        self.climate = climate
        self.terrain = terrain
        self.atmosphere = atmosphere

    def describe_environment(self):
        return f"Climate: {self.climate}, Terrain: {self.terrain}, Atmosphere: {self.atmosphere}"

class AlienCharacter:
    def __init__(self, species, abilities, home_environment):
        self.species = species
        self.abilities = abilities
        self.home_environment = home_environment

    def describe_character(self):
        return f"Species: {self.species}, Abilities: {self.abilities}, Home: {self.home_environment.describe_environment()}"
