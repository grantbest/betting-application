class AlienEnvironment:
    def __init__(self, name, climate, terrain, resources):
        self.name = name
        self.climate = climate
        self.terrain = terrain
        self.resources = resources

    def describe_environment(self):
        return f"Environment: {self.name}, Climate: {self.climate}, Terrain: {self.terrain}, Resources: {self.resources}"


class AlienCharacter:
    def __init__(self, name, species, abilities, home_environment):
        self.name = name
        self.species = species
        self.abilities = abilities
        self.home_environment = home_environment

    def describe_character(self):
        env_description = self.home_environment.describe_environment()
        return f"Character: {self.name}, Species: {self.species}, Abilities: {self.abilities}, Home Environment: [{env_description}]"
