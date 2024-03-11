from object import Object


class Food(Object):
    def collision_detected(self, collisioned) -> None:
        self.visible = 0
        collisioned.update_hunger(30)