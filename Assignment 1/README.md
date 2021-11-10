# Python Robotics Simulator

## _Assignment no. 1 for  the Research Track 1 course_

### Professor [Carmine Recchiuto](https://github.com/CarmineD8)
----------------------
This is a simple, portable robot simulator developed by [Student Robotics](https://studentrobotics.org).

The aim of this project is to make a holonomic robot move around an arena following these rules:
- the robot has to move counter-clockwise;
- the robot must avoid the walls of the arena, made up of golden tokens;
- the robot must approach, grab and release behind itself the silver tokens displaced around the arena.

The following figures show the objects descripted above:

Holonomic robot 

![alt text](https://github.com/sarasgambato/Research_Track_1/blob/main/Assignment%201/images/robot.png)

Golden token

![alt text](https://github.com/sarasgambato/Research_Track_1/blob/main/Assignment%201/images/token.png)

Silver token

![alt text](https://github.com/sarasgambato/Research_Track_1/blob/main/Assignment%201/images/token_silver.png)

Arena

![alt text](https://github.com/sarasgambato/Research_Track_1/blob/main/Assignment%201/images/arena.jpeg)


## Installing and running

The simulator requires a Python 2.7 installation, the [pygame](http://pygame.org/) library, [PyPyBox2D](https://pypi.python.org/pypi/pypybox2d/2.1-r331), and [PyYAML](https://pypi.python.org/pypi/PyYAML/).

Once the dependencies are installed, simply run the `test.py` script to test out the simulator.

To run one (ore more) scripts in the simulator, use `run.py`, passing it the files name as shown in the following code line:
```sh
$ python2 run.py assignment.py
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
   * Returns: this function has no returns.
* `turn(speed, time)`: this function sets the angular velocity of the robot.
   * Arguments: `speed` sets the velocity of the motors, `time` tells the robot the amout of time it has to turn.
   * Returns: this function has no returns.

### <a id="the-grabber"></a> The Grabber ###

The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, the `R.release` method is used.

Cable-tie flails are not implemented.

#### Functions that use these methods ####

* `grab_silver_token()`: function that uses the methods `R.grab` and `R.release` to implement the routine to approach, grab and release the silver token in front of us:

   * Arguments: this function has no argments.
   * Returns: this function has no returns.

The routine to approach, grab and release the token takes place inside a `while(True)` loop.
The function states that if the robot is near the silver token, so if `dist < 1.5`, it approaches the token based on `rot_y`: if the robot is aligned with the token, so if `-a_th <= rot_y <= a_th` (where `a_th` is the orrientation threshold, which is set at 2°) it  slowly goes toward it, otherwise the robot turns left or right to align with the token.
Code implementation:
```python
if dist < 1.5:
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
Once the robot is right in front of the token, so once `dist < d_th` (where `d_th` is the distance threshold, which is set at 0.4), the routine states that the robot grabs it and checks the distance from the closest golden token on the left and on the right of itslef via the function `check_distance()`, descripted in the [next section](#vision). This last control was implemented so that when the robot turns to release the token behind itslef, it does not collide with the walls because it will turn in the direction where there is more space.
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

### <a id="vision"></a> Vision ###

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
One thing that must be taken into note is that the robot has sensors all around itself, so it can detect tokens in a cone of 360° (from -180° to 0° on the left and from 0° to 180° on the right), so a control on the angle between the robot and the tokens must be implemented when looking for golden/silver tokens.

#### Functions that use the `Marker` object and `R.see()` method ####
The `Marker` object and the `R.see()` method have been used by many functions in the simulator:
* `find_golden_token()`: this functions has been implemented to find the golden tokens in front of the robot at a maximum distance of 0.8 and in a cone of 90° (45° on the left and 45° on the right). The goal of this function is to communicate to the main function that the robot is about to hit a wall if it does not turn away.
   * Arguments: this function has no arguments.
   * Returns: the function returns `dist` and `rot_y`, which are respectively the distance and the angle between the robot and the closest golden token. If no golden token is detected in the vicinity of the robot, the function returns `-1` and `-1`.

* `find_silver_token()`: this functions has been implemented to find the silver tokens in front of the robot at a maximum distance of 1.5 and in a cone of 90 degrees (45 degrees on the left and 45 degrees on the right). The goal of this function is to communicate to the main function that a silver token has been found and that the routine to grab it can start.
   * Arguments: this function has no arguments.
   * Returns: the function returns `dist` and `rot_y`, which are respectively the distance and the angle between the robot and the closest silver token. If no silver token is detected in the vicinity of the robot, or if the robot could hit a golden token while trying to approach the detected silver token (checked via the function `golden_obstacle()`), the function returns `-1` and `-1`.

* `check_distance()`: this function has been implemented to check if the closest golden token to the robot is on the left or on the right in a cone of 30°, from -105° to -75° for the left side and from 75° to 105° for the right side. The goal of this function is to make the robot turn left or right based on the return of the function.
   * Arguments: this function has no arguments.
   * Returns: the function returns `1` if the closest golden token is on the right; in this case the robot will turn left. The function return `-1` if the closest golden token is on the left; in this case the robot will turn right.

* `golden_obstacle()`: this function has been implemented to check whether there are golden tokens between the robot and the silver token that has been detected in the function `find_silver_token(dist, rot_y)`.
   * Arguments: this function takes as inputs `dist` and `rot_y`, which are respectively the distance and the angle between the robot and the detected silver token.
   * Returns: the function returns `True` if a golden token is between the silver token and the robot; in this case the calling function will discard the silver token that has been detected. The function returns `False` if the silver token is the closest one; in this case the calling function will save the distanca and the angle of the detected silver token from the robot.

The following code shows the implementation of the function `find_silver_token()` as an example:
```python
def find_silver_token():
    dist = 1.5
    for token in R.see():
        if token.dist < dist and token.info.marker_type == MARKER_TOKEN_SILVER and -45 < token.rot_y < 45:
            if golden_obstacle(token.dist, token.rot_y) == False:	
            	dist = token.dist
            	rot_y = token.rot_y
    if dist == 1.5:
 	return -1, -1
    else:
    	return dist, rot_y
```
## Main function ##
The following flowchart shows the algorithm followed by the robot to look for silver tokens.

![alt text](https://github.com/sarasgambato/Research_Track_1/blob/main/Assignment%201/images/main.png)

As we can see, the robot keeps driving around the arena looking for silver tokens thanks to the `while(1)` loop. Then a series of `if` statements follow in this order:
1) Is a golden token detected? If yes, check if the closest wall is on the left or on the right of the robot and turn until the robot cannot detect golden tokens anymore; if not, go to the next `if` statement.
2) Is a silver token detected? If not, drive forward and keep looking for it; if yes, execute the grab routine descripted in the section relative to [The Grabber](#the-grabber).

## Conclusions ##
### My difficulties ###
Then main difficulties I encountered were:
* Making the robot turn in a proper way when being too close to a wall; this problem was solved by creating a loop in the main function which states that the robot must turn until it does not detect golden token anymore.
* Avoiding considering the silver tokens which would make the robot collide with the wall while trying to grab them; this problem was solved by setting the threshold to look for silver tokens at 1.5 and by creating the function `golden_obstacle()`, descripted [above](#vision).

Also, I've worked very little with GitHub in the previous years, so doing this assignment helped increasing my dexterity with this platform, which is very essential for an engineer.

### Possible improvements ###
Given that the threshold to look for silver tokens is pretty low (set at 1.5), a possible improvement could be adding a control in the function `grab_silver_token()`, instead of controlling the golden tokens between the robot and the silver token inside the function `find_silver_token()`, so that when the robot finds a silver token, it approaches the token while countinuously checking the distance from the wall. I personally tried implementing this using the function `check_distance()` inside the grab routine: it worked for about three loops around the arena, then a golden token was hit, so the algorithm should have been upgraded and the bugs fixed. I choose, instead, to keep the function `golden_obstacle()` because the robot did not hit once the walls in ten loops around the arena (then I stopped the execution of the program via keyboard interrupt, as I was pretty sure that what I choose to do was correct), so the rules of the assignment were respected.

Also, my implementation of the assignment is fairly simple: for example, the turns to not hit the walls are as easy as they could be implemented, so another possible improvement could be making the robot turn more swiftly.

[sr-api]: https://studentrobotics.org/docs/programming/sr/
