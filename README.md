# Python Robotics Simulator

## _Assignment no. 1 for  the Research Track 1 course_

### Professor [Carmine Recchiuto](https://github.com/CarmineD8)
----------------------
This is a simple, portable robot simulator developed by [Student Robotics](https://studentrobotics.org).

The aim of this project is to make a holonomic robot move around an arena following these rules:
- the robot has to move counter-clockwise;
- the robot must avoid the walls of the arena, made up of golden boxes;
- the robot must approach, grab and release behind itself the silver tokens displaced around the arena.

The following figures show the objects descripted above:

Holonomic robot 

![alt text](https://github.com/CarmineD8/python_simulator/blob/assignment/robot-sim/sr/robot.png)

Golden token

![alt text](https://github.com/CarmineD8/python_simulator/blob/assignment/robot-sim/sr/token.png)

Silver token

![alt text](https://github.com/CarmineD8/python_simulator/blob/assignment/robot-sim/sr/token_silver.png)


## Installing and running

The simulator requires a Python 2.7 installation, the [pygame](http://pygame.org/) library, [PyPyBox2D](https://pypi.python.org/pypi/pypybox2d/2.1-r331), and [PyYAML](https://pypi.python.org/pypi/PyYAML/).

Once the dependencies are installed, simply run the `test.py` script to test out the simulator.

To run one (ore more) scripts in the simulator, use `run.py`, passing it the files name as shown in the following code line:
```sh
$ python run.py assignment.py
```

## Robot API

The API for controlling a simulated robot is designed to be as similar as possible to the [SR API][sr-api].

## Features

### Motors ###

The simulated robot has two motors configured for skid steering, connected to a two-output [Motor Board](https://studentrobotics.org/docs/kit/motor_board). The left motor is connected to output `0` and the right motor to output `1`.

The Motor Board API is identical to [that of the SR API](https://studentrobotics.org/docs/programming/sr/motors/), except that motor boards cannot be addressed by serial number. So, to turn on the spot at one quarter of full power, one might write the following:

```python
R.motors[0].m0.power = 25
R.motors[0].m1.power = -25
```
The robot moves thanks to the following implemented functions:
* `drive(speed, time)`: this function sets the linear velocity of the robot.
   * Arguments: `speed` sets the velocity of the motors, `time` tells the robot the amout of time it has to drive forward.
   * Returns: the functions has no returns.
* `turn(speed, time)`: this function sets the angular velocity of the robot.
   * Arguments: `speed` sets the velocity of the motors, `time` tells the robot the amout of time it has to turn.

### The Grabber ###

The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, the `R.release` method is used.

Cable-tie flails are not implemented.

#### Functions that use these methods ####

* `grab_silver_token()`: function that uses the methods `R.grab` and `R.release` to implement the routine to approach, grab and release the silver token in front of us:

   * Arguments: `dist` and `rot_y`, which are respectively the distance of the robot from the silver token and the angle between the two.
   * Returns: the function has no returns.

The function states that if the robot is near the silver token, so if `dist < 2`, it approaches the token based on `rot_y`: if the robot is well aligned with the token, it  slowly goes toward it, otherwise the robot turns left or right to align with the token.
Code implementation:
```python
if dist < 2:
        print("I'm near the token")
        if -a_th<= rot_y <= a_th: 
            print("Ah, here we are!")
            drive(30, 0.1)
        elif rot_y < -a_th: 
            print("Left a bit...")
            turn(-1, 0.5)
        elif rot_y > a_th:
            print("Right a bit...")
            turn(+1, 0.5)
```
Once the robot is right in front of the token, so once `dist < d_th` (where `d_th` is the distance threshold), the routine states that the robot grabs it and checks the distance from the closest golden token on the left and on the right of itslef via the function `check_distance()`, descripted in the next section. This last control was implemented so that when the robot turns to release the token behind itslef, it does not collide with the walls because it will turn in the direction where there is more space.
Code implementation:
```python
if dist < d_th:
        print("Found it!")
        R.grab() 
        print("Gotcha!")
        if check_distance() == 1:
            turn(-20, 3)
            R.release()
            drive(-20, 1)
            turn(20, 3)
        else:
            turn(20, 3)
            R.release()
            drive(-20, 1)
            turn(-20, 3)
        print("Released the silver token, looking for a new one!")
        return
```

### Vision ###

To help the robot find tokens and navigate, each token has markers stuck to it, as does each wall. The `R.see` method returns a list of all the markers the robot can see, as `Marker` objects. The robot can only see markers which it is facing towards.

Each `Marker` object has the following attributes:

* `info`: a `MarkerInfo` object describing the marker itself. Has the following attributes:
  * `code`: the numeric code of the marker.
  * `marker_type`: the type of object the marker is attached to (either `MARKER_TOKEN_GOLD`, `MARKER_TOKEN_SILVER` or `MARKER_ARENA`).
  * `offset`: offset of the numeric code of the marker from the lowest numbered marker of its type. For example, token number 3 has the code 43, but offset 3.
  * `size`: the size that the marker would be in the real game, for compatibility with the SR API.
* `centre`: the location of the marker in polar coordinates, as a `PolarCoord` object. Has the following attributes:
  * `length`: the distance from the centre of the robot to the object (in metres).
  * `rot_y`: rotation about the Y axis in degrees.
* `dist`: an alias for `centre.length`
* `res`: the value of the `res` parameter of `R.see`, for compatibility with the SR API.
* `rot_y`: an alias for `centre.rot_y`
* `timestamp`: the time at which the marker was seen (when `R.see` was called).

For example, the following code lists all of the markers the robot can see:

```python
markers = R.see()
print "I can see", len(markers), "markers:"

for m in markers:
    if m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER):
        print " - Token {0} is {1} metres away".format( m.info.offset, m.dist )
    elif m.info.marker_type == MARKER_ARENA:
        print " - Arena marker {0} is {1} metres away".format( m.info.offset, m.dist )
```
#### Functions that use the `Marker` object and `R.see()` method ####
The `Marker` object and the `R.see()` method have been used by many functions in the simulator:
* `find_golden_token()`: this functions has been implemented to find the golden tokens in front of the robot at a maximum distance of 0.8 and in a cone of 90° (45° on the left and 45° on the right). The goal of this function is to communicate to the main function that the robot is about to hit a wall if it does not turn away.
   * Arguments: this function has no arguments.
   * Returns: the function returns `dist` and `rot_y`, which are respectively the distance and the angle between the robot and the closest golden token. If no golden token is detected in the vicinity of the robot, the function returns `-1` and `-1`.

* `find_silver_token()`: this functions has been implemented to find the silver tokens in front of the robot at a maximum distance of 2 and in a cone of 90 degrees (45 degrees on the left and 45 degrees on the right). The goal of this function is to communicate to the main function that a silver token has been found and that the routine to grab it can start.
   * Arguments: this function has no arguments.
   * Returns: the function returns `dist` and `rot_y`, which are respectively the distance and the angle between the robot and the closest silver token. If no silver token is detected in the vicinity of the robot, or if the robot could hit a golden token while trying to approach the detected silver token, the function returns `-1` and `-1`.

* `check_distance()`: this function has been implemented to check if the closest golden token to the robot is on the left or on the right in a cone of 30°, from -100° to -70° for the left side and from 70° to 100° for the right side. The goal of this function is to make the robot turn left or right based on the return of the function.
   * Arguments: this function has no arguments.
   * Returns: the function returns `1` if the closest golden token is on the right; in this case the robot will turn left. The function return `-1` if the closest golden token is on the left; in this case the robot will turn right.

* `golden_between()`: this function has been implemented to check whether there are golden tokens between the robot and the silver token that has been detected in the function `find_silver_token(dist, rot_y)`.
   * Arguments: this function takes as inputs `dist` and `rot_y`, which are respectively the distance and the angle between the robot and the detected silver token.
   * Returns: the function returns `True` if a golden token is between the silver token and the robot; in this case the calling function will discard the silver token that has been detected. The function returns `False` if the silver token is the closest one; in this case the calling function will save the distanca and the angle of the detected silver token from the robot.

The following code shows the implementation of the function `find_silver_token()` as an example:
```python
def find_silver_token():
    dist = 2
    for token in R.see():
        if token.dist < dist and token.info.marker_type == MARKER_TOKEN_SILVER and -45 < token.rot_y < 45:
            if golden_between(token.dist, token.rot_y) == False:	
            	dist = token.dist
            	rot_y = token.rot_y
    if dist == 2:
 	return -1, -1
    else:
    	return dist, rot_y
```

[sr-api]: https://studentrobotics.org/docs/programming/sr/
