from Box2D import b2BodyDef, b2RevoluteJointDef
from Box2D import b2_dynamicBody, b2PolygonShape
from Box2D import b2Dot, b2Vec2, b2DestructionListener
import numpy
import math

'''
Based on
http://www.iforce2d.net/src/iforce2d_TopdownCar.h
'''


PPM = 1.0
DEGTORAD = 0.0174532925199432957
RADTODEG = 57.295779513082320876

TDC_LEFT = int('0001', 2)
TDC_RIGHT = int('0010', 2)
TDC_UP = int('0100', 2)
TDC_DOWN = int('1000', 2)

FUD_CAR_TIRE = 0
FUD_GROUND_AREA = 1


class FixtureUserData(object):
    '''
    a class to allow subclassing of different fixture user data
    '''

    def __init__(self, m_type):
        self.m_type = m_type

    def getType(self):
        return self.m_type


class CarTireFUD(FixtureUserData):
    '''
    class to allow marking a fixture as a car tire
    '''
    def __init__(self):
        super(CarTireFUD, self).__init__(FUD_CAR_TIRE)


class GroundAreaFUD(FixtureUserData):
    '''
    class to allow marking a fixture as a ground area
    '''
    def __init__(self, fm, ooc):
        super(GroundAreaFUD, self).__init__(FUD_GROUND_AREA)
        self.frictionModifier = fm
        self.outOfCourse = ooc


class TDTire(object):

    def __init__(self, world):
        self.m_maxForwardSpeed = 0
        self.m_maxBackwardSpeed = 0
        self.m_maxDriveForce = 0
        self.m_maxLateralImpulse = 0
        self.m_groundAreas = []

        bodyDef = b2BodyDef()
        bodyDef.type = b2_dynamicBody
        bodyDef.restitution = 0.1
        self.m_body = world.CreateBody(bodyDef)

        polygonShape = b2PolygonShape()
        polygonShape.SetAsBox(0.5, 1.25)
        fixture = self.m_body.CreateFixture(shape=polygonShape, density=5)
        fixture.userData = CarTireFUD()

        self.m_body.userData = self

        self.m_currentTraction = 1

    def __del__(self):
        self.m_body.world.DestroyBody(self.m_body)

    def setCharacteristics(self,
                           maxForwardSpeed,
                           maxBackwardSpeed,
                           maxDriveForce,
                           maxLateralImpulse):
        self.m_maxForwardSpeed = maxForwardSpeed
        self.m_maxBackwardSpeed = maxBackwardSpeed
        self.m_maxDriveForce = maxDriveForce
        self.m_maxLateralImpulse = maxLateralImpulse

    def addGroundArea(self, ga):
        self.m_groundAreas.append(ga)
        self.updateTraction()

    def removeGroundArea(self, ga):
        self.m_groundAreas.remove(ga)
        self.updateTraction()

    def updateTraction(self):
        if (len(self.m_groundAreas) == 0):
            self.m_currentTraction = 1
        else:
            # find area with highest traction
            self.m_currentTraction = 0
            for ga in self.m_groundAreas:
                if (ga.frictionModifier > self.m_currentTraction):
                    self.m_currentTraction = ga.frictionModifier

    def getLateralVelocity(self):
        currentRightNormal = self.m_body.GetWorldVector(b2Vec2(1, 0))
        return (b2Dot(currentRightNormal, self.m_body.linearVelocity)
                * currentRightNormal)

    def getForwardVelocity(self):
        currentForwardNormal = self.m_body.GetWorldVector(b2Vec2(0, 1))
        return (b2Dot(currentForwardNormal,
                self.m_body.linearVelocity)
                * currentForwardNormal)

    def updateFriction(self):
        # lateral linear velocity
        impulse = self.m_body.mass * -self.getLateralVelocity()
        if (impulse.length > self.m_maxLateralImpulse):
            impulse *= self.m_maxLateralImpulse / impulse.length
        self.m_body.ApplyLinearImpulse(
            self.m_currentTraction * impulse,
            self.m_body.worldCenter,
            False)

        # angular velocity
        self.m_body.ApplyAngularImpulse(
            self.m_currentTraction
            * 0.1
            * self.m_body.inertia
            * -self.m_body.angularVelocity,
            False)

        # forward linear velocity
        currentForwardNormal = self.getForwardVelocity()
        currentForwardSpeed = currentForwardNormal.Normalize()
        dragForceMagnitude = -2 * currentForwardSpeed
        self.m_body.ApplyForce(
            self.m_currentTraction *
            dragForceMagnitude *
            currentForwardNormal,
            self.m_body.worldCenter,
            False)

    def updateDrive(self, controlState):
        # find desired speed
        desiredSpeed = 0
        switch = (controlState & (TDC_UP | TDC_DOWN))
        if (switch == TDC_UP):
            desiredSpeed = self.m_maxForwardSpeed
        elif (switch == TDC_DOWN):
            desiredSpeed = self.m_maxBackwardSpeed
        else:
            return  # do nothing

        # find current speed in forward direction
        currentForwardNormal = self.m_body.GetWorldVector(b2Vec2(0, 1))
        currentSpeed = b2Dot(self.getForwardVelocity(), currentForwardNormal)

        # apply necessary force
        force = 0
        if (desiredSpeed > currentSpeed):
            force = self.m_maxDriveForce
        elif (desiredSpeed < currentSpeed):
            force = -self.m_maxDriveForce
        else:
            return
        self.m_body.ApplyForce(
            self.m_currentTraction
            * force
            * currentForwardNormal,
            self.m_body.worldCenter,
            True)

    def updateTurn(self, controlState):
        desiredTorque = 0
        switch = (controlState & (TDC_LEFT | TDC_RIGHT))
        if (switch == TDC_LEFT):
            desiredTorque = 5
        elif (switch == TDC_RIGHT):
            desiredTorque = -5
        self.m_body.ApplyTorque(desiredTorque)


class TDCar(object):

    def __init__(self, world):
        self.m_tires = []

        # create car body
        bodyDef = b2BodyDef()
        bodyDef.type = b2_dynamicBody
        bodyDef.restitution = 0.1
        self.m_body = world.CreateBody(bodyDef)
        self.m_body.angularDamping = 5

        vertices = []
        for i in xrange(8):
            vertices.append(b2Vec2())
        vertices[0].Set(3, 0)
        vertices[1].Set(6, 5)
        vertices[2].Set(5.6, 11)
        vertices[3].Set(2, 20)
        vertices[4].Set(-2, 20)
        vertices[5].Set(-5.6, 11)
        vertices[6].Set(-6, 5)
        vertices[7].Set(-3, 0)
        polygonShape = b2PolygonShape(vertices=vertices)
        self.m_body.CreateFixture(
            shape=polygonShape,
            density=100.0,
        )

        # prepare common joint parameters
        jointDef = b2RevoluteJointDef()
        jointDef.bodyA = self.m_body
        jointDef.enableLimit = True
        jointDef.lowerAngle = 0
        jointDef.upperAngle = 0
        jointDef.localAnchorB.SetZero()  # center of tire

        maxForwardSpeed = 150
        maxBackwardSpeed = -40
        backTireMaxDriveForce = 50
        frontTireMaxDriveForce = 100
        backTireMaxLateralImpulse = 1.5
        frontTireMaxLateralImpulse = 0.5

        # back left tire
        tire = TDTire(world)
        tire.setCharacteristics(
            maxForwardSpeed,
            maxBackwardSpeed,
            backTireMaxDriveForce,
            backTireMaxLateralImpulse)
        jointDef.bodyB = tire.m_body
        jointDef.localAnchorA.Set(-6, 1.5)
        world.CreateJoint(jointDef)
        self.m_tires.append(tire)

        # back right tire
        tire = TDTire(world)
        tire.setCharacteristics(
            maxForwardSpeed,
            maxBackwardSpeed,
            backTireMaxDriveForce,
            backTireMaxLateralImpulse)
        jointDef.bodyB = tire.m_body
        jointDef.localAnchorA.Set(6, 1.5)
        world.CreateJoint(jointDef)
        self.m_tires.append(tire)

        # front left tire
        tire = TDTire(world)
        tire.setCharacteristics(
            maxForwardSpeed,
            maxBackwardSpeed,
            frontTireMaxDriveForce,
            frontTireMaxLateralImpulse)
        jointDef.bodyB = tire.m_body
        jointDef.localAnchorA.Set(-6, 17)
        self.flJoint = world.CreateJoint(jointDef)
        self.m_tires.append(tire)

        # front right tire
        tire = TDTire(world)
        tire.setCharacteristics(
            maxForwardSpeed,
            maxBackwardSpeed,
            frontTireMaxDriveForce,
            frontTireMaxLateralImpulse)
        jointDef.bodyB = tire.m_body
        jointDef.localAnchorA.Set(6, 17)
        self.frJoint = world.CreateJoint(jointDef)
        self.m_tires.append(tire)

    def __del__(self):
        for i in xrange(len(self.m_tires)):
            self.m_tires[i] = None

    def GetDirection(self):
        '''
        1 for forward
        -1 for backward
        0 for stopped
        '''
        vel = self.m_body.linearVelocity
        angle = -self.m_body.angle
        y = vel.x * math.sin(angle) + vel.y * math.cos(angle)
        ret = 0
        if (y > 0):
            ret = 1
        elif (y < 0):
            ret = -1
        return ret

    def GetAllBodies(self):
        ret = []
        ret.append(self.m_body)
        for tire in self.m_tires:
            ret.append(tire.m_body)
        return ret

    def update(self, controlState, breaking):
        for i in xrange(len(self.m_tires)):
            self.m_tires[i].updateFriction()
        for i in xrange(len(self.m_tires)):
            if (breaking):
                self.m_body.linearDamping = 0.01
            else:
                self.m_body.linearDamping = 0.001
                self.m_tires[i].updateDrive(controlState)

        # control steering
        lockAngle = 35 * DEGTORAD
        turnSpeedPerSec = 60 * DEGTORAD  # from lock to lock in 0.5 sec
        turnPerTimeStep = turnSpeedPerSec / 60.0
        desiredAngle = 0
        switch = (controlState & (TDC_LEFT | TDC_RIGHT))
        if (switch == TDC_LEFT):
            desiredAngle = lockAngle
        elif (switch == TDC_RIGHT):
            desiredAngle = -lockAngle
        angleNow = self.flJoint.angle * 0.95
        angleToTurn = desiredAngle - angleNow
        angleToTurn = numpy.clip(angleToTurn, -turnPerTimeStep, turnPerTimeStep)
        newAngle = angleNow + angleToTurn
        self.flJoint.SetLimits(newAngle, newAngle)
        self.frJoint.SetLimits(newAngle, newAngle)


class MyDestructionListener(b2DestructionListener):
    def SayGoodbye(self, fixture):
        pass
