import statistics


class Coalition:
    def __init__(self, color: (int, int, int), members) -> None:
        self.color = color
        self.members = []

        self.total_hunger = 0
        self.total_max_hunger = 0
        for member in members:
            self.add_player(member=member)

    def __str__(self) -> str:
        return str(self.color)

    def add_player(self, member) -> None:
        if member not in self.members:
            self.members.append(member)
            member.color = self.color
            member.coalition = self

    def remove_player(self, member) -> None:
        self.members.remove(member)
        member.color = (0, 0, 255)
        member.coalition = None
        if len(self.members) == 1:
            self.disband_coalition()

    def average_health(self) -> float:
        """
        Bereken de verhouding van de huidige health to maximum health voor alle players in de coalitie.

        :return: float
        """
        total_health, total_max_health = 0, 0
        for agent in self.members:
            total_health += agent.health
            total_max_health += agent.max_health
        return total_health / total_max_health

    def average_food(self) -> float:
        """
        Bereken de verhouding van de huidige hongerniveau tot maximum hongerniveau voor alle players in de coalitie.

        :return: float
        """
        total_food, total_max_food = 0, 0
        for agent in self.members:
            total_food += agent.hunger
            total_max_food += agent.max_hunger
        return total_food / total_max_food

    def total_strength(self) -> int:
        total_strength = 0
        for agent in self.members:
            total_strength += agent.agent_values['Strength']
        return total_strength

    def total_resourcefulness(self) -> int:
        total_resourcefulness = 0
        for agent in self.members:
            total_resourcefulness += agent.agent_values['Resourcefulness']
        return total_resourcefulness

    def disband_coalition(self) -> None:
        for member in self.members:
            self.remove_player(member=member)

    def determine_diversity(self) -> float:
        strength_values = [member.agent_values['Strength'] for member in self.members]
        resourcefulness_values = [member.agent_values['Resourcefulness'] for member in self.members]

        if len(strength_values) < 2 or len(resourcefulness_values) < 2:
            return 0

        strength_diversity = statistics.stdev(strength_values)
        resourcefulness_diversity = statistics.stdev(resourcefulness_values)

        return (strength_diversity + resourcefulness_diversity) / 2