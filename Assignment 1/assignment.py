from __future__ import print_function
 
import time
import math
from sr.robot import *
 
 
a_th = 2.0
""" float: threshold for the control of the orientation"""
 
d_th = 0.4
""" float: threshold for the control of the linear distance"""
 
R = Robot()
""" instance of the class Robot"""
            
################################################################
 
def drive(speed, seconds):
    """
    Function for setting a linear velocity
     
    Arguments:	
    	speed (int): the speed of the wheels
    	seconds (int): the time interval
    	
    This function has no returns
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
            
################################################################

def turn(speed, seconds):
    """
    Function for setting an angular velocity
     
    Arguments:	
    	speed (int): the speed of the wheels
    	seconds (int): the time interval
    	
    This function has no returns
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0
           
################################################################ 
 
def find_silver_token():
    """
    Function to find the silver closest token
    
    This function has no arguments
 
    Returns:
    	dist (float): distance of the closest silver token (-1 if no token is detected)
    	rot_y (float): angle between the robot and the token (-1 if no token is detected)
    """
    dist = 2
    for token in R.see():
        if token.dist < dist and token.info.marker_type == MARKER_TOKEN_SILVER and -45 < token.rot_y < 45:
        
            # the robot checks whether the detected silver token is behind a wall
            # if not, the parameters of the token are updated
            if golden_between(token.dist, token.rot_y) == False:	
            	dist = token.dist
            	rot_y = token.rot_y
            
    if dist == 2:
 	return -1, -1
 	
    else:
    	return dist, rot_y
            
################################################################
 
def find_golden_token():
    """
    Function to find the closest golden token in front of the robot
    
    This function has no arguments
 
    Returns:	
    	False: no golden token is detected in front of the robot
    	True: a golden token is detected in front of the robot
    """
    dist = 0.8
    for token in R.see():
        if token.dist < dist and token.info.marker_type == MARKER_TOKEN_GOLD and -45 < token.rot_y < 45:
            dist = token.dist
            rot_y = token.rot_y
            
    if dist == 0.8:
 	return False
 	    
    else:
    	return True
            
################################################################    

def check_distance():
    """
    Function to check whether the closest golden token is on the left or on the right of the robot
    
    This function has no arguments
    
    Returns:
    	1: the closest golden token is on the right
    	-1: the closest golden token is on the left
    """
    
    dist = 15
    for token in R.see():
        if token.dist < dist and token.info.marker_type == MARKER_TOKEN_GOLD and (70 < token.rot_y < 100 or -100 < token.rot_y < -70):
            dist = token.dist
            rot_y = token.rot_y
            
    if rot_y > 0:
    	return 1
    	
    else:
    	return -1

################################################################
    
def golden_between(dist, rot_y):
    """
    Function to check whether there are golden tokens between the robot and the silver token dected
    
    Arguments:
    	dist (float): distance of the closest silver token
    	rot_y (float): angle between the robot and the token
    
    Retunrs:
    	True: a golden token is between the robot and the silver token
    	False: the detected silver token is closer than any other token
    """
    
    th_dist = 2;
    for token in R.see():
        if token.dist < th_dist and token.info.marker_type == MARKER_TOKEN_GOLD and abs(token.rot_y) < abs(rot_y):
            th_dist = token.dist
            
    if th_dist == 2 or th_dist > dist:
    	return False
    	
    else:
    	return True
    
################################################################
     
def grab_silver_token(dist, rot_y):
    """
    Function to grab and release the closest silver token
    
    Arguments:	
    	dist (float): distance of the closest silver token
    	rot_y (float): angle between the robot and the token
    	
    This function has no returns
    """

    # if the robot is close to the silver token, it grabs the token
    if dist <d_th:
        print("Found it!")
        R.grab() 
        print("Gotcha!")
        
        # the robot checks the distance from the closest golden token on the left and on the right
        # based on the distance, the robot turns left or right so it does not hit the walls while turning
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
        
    # if the robot is near the token, it moves according to the angle detected between it and the token
    elif dist < 2:
        print("I'm near the token")
        
        # if the robot is well aligned with the token, it goes forward
        if -a_th<= rot_y <= a_th: 
            print("Ah, here we are!")
            drive(50, 0.1)
            
        # if the robot is not well aligned with the token, it moves left or right to allign with it
        elif rot_y < -a_th: 
            print("Left a bit...")
            turn(-1, 0.5)
        elif rot_y > a_th:
            print("Right a bit...")
            turn(+1, 0.5)
            
################################################################

def main():

    # infinite loop to look for silver tokens
    while 1:
	
	# if the robot does not detect golden tokens, it looks for silver tokens
	if find_golden_token() == False: 
	    print("The way is clear!")
	    dist, rot_y = find_silver_token()
			
	    # if a silver token is detected, the robot approaches it to grab it
	    if dist != -1:
		grab_silver_token(dist, rot_y)
					
	    # if a silver token is not detected, the robot continues looking for it
	    else:
	        drive(100, 0.1) 
	        print("I don't see any silver token!")
	                	
        # if the robot detects a golden token, it turns left or right so that it does not collide with the wall
      	else:	
        	
	    # if the robot is too close to a wall on its right, it turns left
	    if check_distance() == 1:
		while find_golden_token():
		    print("I'm too close, turn left")
		    turn(-10, 0.5)
		    	
	    # if the robot is too close to a wall on its left, it turns right
	    else:
		while find_golden_token():
	    	    print("I'm too close, turn right")
	    	    turn(10, 0.5)
		
#################################################################

main()
