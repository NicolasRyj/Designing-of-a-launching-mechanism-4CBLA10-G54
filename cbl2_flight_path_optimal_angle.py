import matplotlib.pyplot as plt
import numpy as np
# Constants
gravity = 9.81  # acceleration due to gravity (m/s^2)
air_density = 1.225  # air density (kg/m^3)
drag_coefficient = 0.3  # drag coefficient (typical for a styrofoam plane)
styrofoam_plane_mass = 0.01  # mass of the styrofoam plane (kg)
initial_velocity = 3.6  # initial velocity (m/s)
lift_coefficient = 0.3  # lift coefficient (adjust as needed)
wing_area = 0.0545 # Our styrofoam plane's wing area
reference_area = 0.0206 # Reference area, for the drag of the plane
max_angle = 25
min_angle = 0
dt = 0.001  # time step (s)
# Initialize lists to store position and velocity data
time_points, x_points, y_points, vx_points, vy_points, angle_points = [], [], [], [], [], []
colors = ['red', 'green', 'blue', 'purple', 'orange']

def lift_force_f(velocity):
    retlift = lift_coefficient*wing_area*air_density*velocity**2/2
    return retlift

def drag_force_f(velocity):
    retdrag = drag_coefficient*reference_area*air_density*velocity**2/2
    if velocity<0:
        retdrag*=-1
    return retdrag

def main():    
    optimal_angle = 0
    travelled_distance_max_current = 0
    print("Input values: \nDrag coefficient: {}\nPlane mass: {}\nInitial velocity: {}\nLift coefficient: {}".format(drag_coefficient, styrofoam_plane_mass, initial_velocity, lift_coefficient))
    print("wing_area: {}\nreference_area: {}\nInitial angle {}. Max angle: {}\nTime step: {}".format(wing_area, reference_area, min_angle, max_angle, dt))
    for current_testing_launch_angle in range(abs(max_angle-min_angle)):
        current_testing_launch_angle = np.radians(min_angle+current_testing_launch_angle)
        # Revert to Initial conditions
        t, x, y = 0.0, 0.0, 1.7
        vx = initial_velocity * np.cos(current_testing_launch_angle)
        vy = initial_velocity * np.sin(current_testing_launch_angle)
        vnet = initial_velocity
        plane_current_angle = np.radians(current_testing_launch_angle)
        time_pointstemp, x_pointstemp, y_pointstemp, vx_pointstemp, vy_pointstemp = [], [], [], [], []
        while y>0:
            time_pointstemp.append(t)
            x_pointstemp.append(x)
            y_pointstemp.append(y)
            vx_pointstemp.append(vx)
            vy_pointstemp.append(vy)
            # Calculate forces
            gravitational_force = -styrofoam_plane_mass * gravity
            drag_force = drag_force_f(vnet)
            lift_force = lift_force_f(vnet)
            net_fy = gravitational_force+lift_force*np.cos(plane_current_angle)
            net_fx = -drag_force*np.cos(plane_current_angle)+lift_force*-np.sin(plane_current_angle)*0.3
            if plane_current_angle < 0:
                net_fx+=+lift_force*-np.sin(plane_current_angle)
            # Calculate acceleration
            ax = net_fx / styrofoam_plane_mass
            ay = net_fy / styrofoam_plane_mass
            # Update velocity and position using Euler's method
            if not abs(ax * dt) > 1000: #If overflow or other error, use last step value and skip step. Good approximation
                vx += ax * dt
                vy += ay * dt
                x += vx * dt
                y += vy * dt
                vnet = np.sqrt(vx**2+vy**2)
            else:
                x += x_points[-1]-x_points[-2]
                y += y_points[-1]-y_points[-2]
                vx += vx_points[-1]-vx_points[-2]
                vy += vy_points[-1]-vy_points[-2]
                break
            plane_current_angle = np.arctan(vy/vx)
            t += dt
        print("Current longest distance: {} m, Distance calculated for angle {} equal to {}".format(travelled_distance_max_current, np.degrees(current_testing_launch_angle), x))
        if travelled_distance_max_current<abs(x):
            travelled_distance_max_current=abs(x)
            optimal_angle=current_testing_launch_angle
        time_points.append(time_pointstemp)
        x_points.append(x_pointstemp)
        y_points.append(y_pointstemp)
        vx_points.append(vx_pointstemp)
        vy_points.append(vy_pointstemp)
    print("=========\nOptimal launch angle calculated to be equivalent to {}, with theoretical distance reached being {}".format(np.degrees(optimal_angle), travelled_distance_max_current))
    return np.degrees(optimal_angle)

if __name__ == '__main__':
    best_angle = main()
    print("Visualising data on Matplot graph.")
    plt.figure()
    for i in range(len(x_points)):
        b = i%6-1
        if i%5 == 0:
            plt.plot(x_points[i],y_points[i], label = 'Launch angle %s'%i, color='black')
        else:
            plt.plot(x_points[i],y_points[i], color=colors[b])
    plt.title("Plane flight path calculations. Optimal angle {} degrees".format(best_angle))
    plt.xlabel("Distance (m)")
    plt.ylabel("Height (m)")
    plt.grid(True)
    plt.show()