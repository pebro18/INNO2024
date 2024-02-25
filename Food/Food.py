class FoodObj:
    """Food class represents a food item in the game. It has a name, quality, and quantity.
     Attributes:
        name (str): The name of the food item.
        food_points (int): The amount of hunger points the food item restores.
        quantity (int): The quantity of the food item."""
    def __init__(self, name :str, food_points : int, quantity : int ):
        self.name = name
        self.points = food_points
        self.quantity = quantity
        self.eaten = False

    def use_food(self):
        if self.quantity > 0:
            self.quantity -= 1
            return self.points
        return 0

    def __str__(self):
        return f"{self.name} {self.points} {self.quantity}"
    
    def __repr__(self):
        return f"{self.name} {self.points} {self.quantity}"