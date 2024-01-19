'''
The idea is the beginning we want to pull the load so it gets started.
Then we want to gradually increase the ratio. However the ratio should
never go below a certain value when the torque is less than the minimum force required.
This means we can get two values. The smallest gear ratio, and the biggest gear ratio.
The rest is just a nautilus gear going from smallest radius to biggest radius.
'''
import math
import matplotlib.pyplot as plt
import os
import subprocess
import decimal

#Settings for this code
plt.interactive( False )

# Setting how much precision we want. the greater the precision, the harder it is to calculate.
# 5 is to prevent math module errors.
decimal.getcontext().prec = 6

#Consants - Update for desired results
gravity = 9.81              #ms^-1
plane_weight = 0.048        #Kg
cart_weight = 0.08           #Kg
bolt_load = 0.21            #Kg
ramp_angle = 15             #deg
air_res = 0                 #N
load_dropping_height = 1.5  #m
lift_caused_by_plane = 0    #Nms^-1 ! For a more advanced model, plane lift can be considered, reducing friction on ramp
impulse_time = 1.2          #s      ! Time of change in momentum when string holding load is in tension
angle_step_value = 1        #       ! Change this for precision of sketch
multip_big_gear_factor = 1  #       ! How big the gear should be

#Matplotlib values
top=0.88,
bottom=0.225,
left=0.055,
right=0.99,
hspace=0.2,
wspace=0.2


#Friction forces experienced that slow down the plane or cart
friction_forces = [[
    "Ramp bottom friction",
    ramp_angle,
    0.2, #Static Friction coefficient
    0.1, #Dynamic Friction coefficient
    plane_weight + cart_weight-lift_caused_by_plane
],
[
    "Gearbox friction",
    0,
    0.01,
    0.005,
    1
]]


e_pot_load = gravity*load_dropping_height*bolt_load #Potential energy of the load. Could be used in future to account for impulse or to predict final velocity

def resistance_caused_load(friction_coefficients_and_normals = []):
    '''
    This function returns the total static and dynamic friction force in newtons due to resitance.
    It calculates the value by compiling it from a list of given values. The list has to follow the
    'friction_forces' list to work correcly.
    '''
    print("Calculating friction forces...")
    friction_force_beginning_max = 0
    friction_force_after_beginning_max = 0
    for p in friction_coefficients_and_normals:
        specific_value_force_beginning = math.sin(math.radians(p[1]))*p[2]*p[4]
        specific_value_force_after_beginning = math.sin(p[1])*p[3]*p[4]
        friction_force_beginning_max += specific_value_force_beginning
        friction_force_after_beginning_max += specific_value_force_after_beginning
        print("$ added forces for {} |STATIC|. Value: {} |DYNAMIC|. Value: {}".format(p[0], specific_value_force_beginning, specific_value_force_after_beginning))
    final_return_resistance = [friction_force_beginning_max, friction_force_after_beginning_max]
    print("Return value: {}".format(final_return_resistance))
    return final_return_resistance #Returns a list with element 0 being static friction force and element 1 being dynamic friction force

def impulse_based_force(height, weight, impulse_time):
    '''
    This function returns the value of the impulse.
    It is not yet complete and clear how to get the impluse time, 
    so this function is unusable in the current context, 
    but could be used in the future.
    '''
    print("Calculating Impulse...")
    impulse_force = weight*math.sqrt(2*gravity*height)/impulse_time
    print("Impulse found to be {}".format(impulse_force))
    return impulse_force #Returns a number in newtons

def plane_caused_load(angleRamp, weightplane, air_resistance = 0):
    '''
    This function returns one value that gives the net load caused by the plane itself, 
    given all the seperate values.
    '''
    print("Calculating plane caused load...")
    plane_force = math.cos(math.radians(angleRamp)) * weightplane + air_resistance
    print("Calculated plane caused load to be {}".format(plane_force))
    return plane_force #Returns a number in newtons

def gearratio(force_required_high, force_required_low, load_force_min, load_force_max):
    '''
    This function returns the ratio of the gears for later manufacturing. The ratios returned are simply the smaller and bigger ratios. 
    All the ratios in between will be increasing with a rate of change determined in the get_gear_points_in_space() function according
    to the desired shape of the gear.
    '''
    print("Calculating gear ratio...")
    small_gear_ratio = force_required_high/load_force_max
    big_gear_ratio = force_required_low/load_force_min
    print('Calculated gear ratios: Small => {}, Big => {}'.format(small_gear_ratio, big_gear_ratio))
    return [small_gear_ratio, big_gear_ratio] #Returns a list with element 0 the smallest gear ratio and element 1 the biggest gear ratio

def get_gear_points_in_space(ratios_calculated, dtheta):
    '''
    This function gets the difference between the smaller and greater radius found in the gearratio() function.
    The desired precision of calculation can be set with the dtheta value. a good enough value is $1$ degree as dtheta.
    The function supposes the change in radius over the change in angle is constant. Ideal nautilus gears do not exactly follow
    this approach but the result give good enough results.
    '''
    small_radius = ratios_calculated[0]
    big_radius = ratios_calculated[1]
    print("Getting gear points in space...")
    return_list_angles_and_radius = []
    return_list_cartasian_coords = []
    net_change_of_radius = big_radius-small_radius
    number_of_return_points = int(360/dtheta)
    print("Number of points: {}".format(number_of_return_points))
    dr=net_change_of_radius/number_of_return_points
    print("Δθ = {}, Δr = {}".format(dtheta, dr))
    for i in range(number_of_return_points+1):
        radius_for_theta = [i, small_radius+i*dr*multip_big_gear_factor, big_radius-i*dr*multip_big_gear_factor, dtheta*i]
        print("Point {} | Increasing Radius => {}. Decreasing Radius => {}. '''int(decimal.Decimal)''' ".format(i, radius_for_theta[1], radius_for_theta[2]))
        return_list_cartasian_coords.append([math.cos(math.radians(radius_for_theta[3]))*radius_for_theta[1]*multip_big_gear_factor, math.sin(math.radians(radius_for_theta[3]))*radius_for_theta[1]*multip_big_gear_factor, i])
        return_list_angles_and_radius.append(radius_for_theta)
    return [return_list_angles_and_radius, return_list_cartasian_coords]

def get_radius_lenght(points):
    '''
    This function gets the lenght of the outer radius of the nautilus gear by computing the distance between point i and i+1
    using pythagorus theorem. Gives very close approximation of the lenght. The smaller the dtheta chosen in the 
    get_gear_points_in_space() function, the better the approximation.
    '''
    print('$Calculating rad len')
    total_length = 0
    for i in range(len(points)-1):
        if not points[i][2] == len(points)-1:
            print('Lenght P_{} ({}) -> P_{} ({}):'.format(points[i][2], points[i], int(points[i][2])+1, points[int(points[i][2])+1]))
        try:
            dx = abs((points[i+1][0]-points[i][0]))
            dy = abs((points[i+1][1]-points[i][1]))
            increase_radius=math.sqrt(
                    dx**2+dy**2
                )
            plt.plot([total_length, 0], [total_length+increase_radius,0], marker='o')
            total_length+=increase_radius
        except Exception as e:
            print("Calculation too complex. Approx made; Change precision decimal places to lower number in constants!")
            print(e)
            total_length+=math.sqrt(
                    (points[points[i][2]][0]-points[i][0])**2+(points[points[i][2]-1][1]-points[i][1])**2
                )
        print(total_length)
    return total_length

def drawgear(points, radius_lenght):
    '''
    This function simply helps visualise the shape of the gear on a graph. 
    It uses the cartesian coordinates calculated elsewhere and just draws all the points from the center (0, 0).
    It also draws a line from the center to the first and last points.
    '''
    print('Visualising gear shape')
    plt.plot([0, points[len(points)-1][0]], [0, points[len(points)-1][1]], marker='o') #Center point
    plt.plot([0, radius_lenght], [0, 0], marker='o') #Radius Visualization
    for i in range(len(points) - 1):
        point1 = points[i]
        point2 = points[i + 1]
        plt.plot([point1[0], point2[0]], [point1[1], point2[1]], marker='o')
    return

def get_velocity_from_ratio(ratio, height_load):
    '''
    This function returns the theoretical output velocity of the mechanism. This however doesn not account
    for the impulse based changes in speed, which are too complex to calculate. it also takes the average acceleration, possibly chaninging the result
    This result of this function should only be taken as an approximate calculation
    '''
    print('Calculating output velocity given inputed values')
    arv_ratio = ratio[0]/3 + 2*ratio[1]/3
    out_str = math.sqrt(2*(gravity*arv_ratio)*height_load)
    print(str(out_str) + 'ms^-1')
    return out_str

def save_to_txt(items_to_store, file_path):
    '''
    This function saves all the points with all necessary data and shows for copying to later use in a CAD
    software such as Fusion 360. A separate script will need to be written.
    '''
    file_path=str(file_path)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass
    
    with open(file_path, 'w') as file:
        open(file_path, 'w').close()
        file.write(str('['))
        for item in items_to_store:
            file.write(str(item) + ',\n')
        file.write(str(']'))


    print('Saved data to {}'.format(file_path))

    try:
        subprocess.Popen(['notepad.exe', file_path])
    except Exception as e:
        print("Failed file openning: {}".format(e))

    if True:
    #try:
        # Here all of the functions are called in correct order. All that needs to be done to get the desired values is update the constants table.
        resistance_of_everything = resistance_caused_load(friction_forces)
        plane_load_force = plane_caused_load(ramp_angle, plane_weight, air_res)
        net_force_to_pull_max = resistance_of_everything[0] + plane_load_force
        net_force_to_pull_min = resistance_of_everything[1] + plane_load_force
        ratios_result = gearratio(net_force_to_pull_max, net_force_to_pull_min, bolt_load, bolt_load+impulse_based_force(load_dropping_height, bolt_load, impulse_time))
        resultgear = get_gear_points_in_space(ratios_result, angle_step_value)
        print("Obtained gear ratio for small and big {}".format(ratios_result))
        radius_net_lenght = get_radius_lenght(resultgear[1])
        print("Net Radius Lenght = {}".format(radius_net_lenght))
        #Saving to external files
        save_to_txt(resultgear[1], './gear_points.txt')
        get_velocity_from_ratio(ratios_result, load_dropping_height)
        #Visualising the gear
        drawgear(resultgear[1], radius_net_lenght)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.grid(True)
        plt.title('Gear Ratio {} {}'.format(ratios_result[0], ratios_result[1]))
        plt.show()
        print("POTENTIAL UPDATE TO SCRIPT: INSTEAD OF LINEAR CHANGE IN RADIUS, MAKE IT REVERSE QUADRATIC")
    #except Exception as e:
        # If an error occurs, the script will shut down, printing the reason.
    #    print("Failed:", e)


'''
The result gives a gear that is to be attached to the same gear of same shape, just at scale one relative to the gear ratio. if the ratio is 0.5, the main gear will be half the size x of secondary gear
'''