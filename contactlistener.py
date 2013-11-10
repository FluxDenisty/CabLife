from Box2D import b2ContactListener
from car import CarTireFUD
from mapobject import MapObject


class ContactListener(b2ContactListener):

    def __init__(self, textSystem, car):
        b2ContactListener.__init__(self)
        self.textSystem = textSystem
        self.playerCar = car

    def handleContact(self, contact, began):
        if (not began):
            return
        a = contact.fixtureA
        b = contact.fixtureB
        fudA = a.userData
        fudB = b.userData

        player = None
        other = None
        if (type(fudA) == CarTireFUD):
            player = fudA
            other = fudB
        elif (type(fudB) == CarTireFUD):
            player = fudB
            other = fudA

        if (player is None or other is None or player.car is not self.playerCar):
            return

        if (type(other) == MapObject):
            if (self.textSystem.state == "find" and other.name == "pickup"):
                self.textSystem.pickup(other)
            if (self.textSystem.state == "driving" and other.name == "pickup"):
                self.textSystem.dropoff(other)

    def BeginContact(self, contact):
        self.handleContact(contact, True)

    def EndContact(self, contact):
        self.handleContact(contact, False)

    def tire_vs_groundArea(tireFixture, groundAreaFixture, began):
        tire = tireFixture.body.userData
        gaFud = groundAreaFixture.userData
        if (began):
            tire.addGroundArea(gaFud)
        else:
            tire.removeGroundArea(gaFud)
