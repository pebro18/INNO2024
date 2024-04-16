from object import Object


class Food(Object):
    def collision_detected(self, collisioned) -> None:
        self.visible = 0
        if collisioned.coalition is not None:
            food_amount = 30 * collisioned.agent_values["Resourcefulness"] // len(collisioned.coalition.members)
            for member in collisioned.coalition.members:
                member.update_hunger(amount=food_amount)
        else:
            collisioned.update_hunger(amount=30 * collisioned.agent_values["Resourcefulness"])