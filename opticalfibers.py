import numpy as np
import matplotlib.pyplot as plt 
plt.style.use('dark_background')

# --- Step 1: Classes
class Fiber:
    # Stores the properties of an optical fiber, such as core diameter, cladding diameter, and numerical aperture

    def __init__(self, n_core=1.5, n_cladding=1.4, radius=30.0, length=500.0):   # __init__ : a method to initialize the attributes of the class. self: refers to the instance of the class being created.
        self.n_core = n_core                     # Refractive index of the core
        self.n_cladding = n_cladding             # Refractive index of the cladding
        self.radius = radius                     # Radius of the core ( defines the fiber core boundaries at y = ±radius )
        self.length = length                     # Length of the fiber ( defines the fiber length along the x-axis from 0 to length )

class Ray:
    # Represents a light ray with its position, direction and angle
    def __init__(self, pos, angle_deg, fiber):
    # Initialize position as a numpy array for easier calculations, convert angle from degrees to radians, and store a reference to the fiber
        self.pos = np.array(pos, dtype=float)    # Position of the light ray (x, y)
        self.angle = np.radians(angle_deg)       # Convert angle from degrees to radians
        
        ux = np.cos(self.angle)             # Unit vector in the x-direction based on the angle
        uy = np.sin(self.angle)             # Unit vector in the y-direction based on the angle

        self.direction = np.array([ux, uy]) / np.sqrt(ux**2 + uy**2)   # Store Direction vector of the light ray based on the angle

        self.fiber = fiber                       # Reference to the Fiber object for accessing its properties
  #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------  
       


    # --- Step 2: Geometric Logic For Exact Intersection of Light Rays with Fiber Boundaries
    
    def find_exact_boundary_intersection(self):
        # Calculate the exact intersection of the light ray with the fiber boundaries (core-cladding interface)

        pos = self.pos                 # Current position of the ray 
        ux, uy = self.direction        # Direction vector of the ray
        R = self.fiber.radius          # Radius of the fiber core
    
        #Check if he ray is moving towards the upper boundary (y = +R) or the lower boundary (y = -R) and calculate the intersection point accordingly

        if uy > 0 :                                         # Moving towards upper boundary
            boundary_y = R
        elif uy < 0 :
            boundary_y = -R                                 # Moving towards lower boundary
        else:
            return None                                     # Ray is parallel to the boundaries, no intersection
        
        # Calculate the parameter t for the ray equation to find the intersection point
        # The ray equation is given by: pos + t * direction, where t is the distance along the ray's direction vector to the intersection point
        try :
            t = (boundary_y - pos[1]) / uy                     # Calculate t using the y-component of the ray's direction and position
        except ZeroDivisionError:
            return None                                     # Handle the case where uy is zero (ray is parallel to boundaries)
        
        if t <= 0:
            return None                                       # Ray is not heading towards the boundary in the forward positive direction
        
        # Calculate the intersection point using the ray equation 
        x_int = pos[0] + t*ux     # Calculate the intersection point using the ray's position and direction
        y_int = boundary_y        # The y-coordinate of the intersection is the boundary_y (either +R or -R)

        return np.array([x_int, y_int])  # Return the intersection point as a numpy array
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-- Step 3 : Reflecton Logic for Light Rays at Fiber Boundaries

def handle_boundary_reflection(pos, current_dir, fiber):
    # Checks the TIR condition and returns the reflected direction when the ray remains trapped.
    # If the incident angle is below the critical angle, the ray refracts into the cladding and is considered leaked.

    ux, uy = current_dir
    n1 = fiber.n_core
    n2 = fiber.n_cladding

    if n1 <= n2:
        return None  # No TIR possible when core index is not greater than cladding index.

    critical_angle = np.arcsin(n2 / n1)

    # The boundary normal is vertical, so the incident angle relative to the normal is arccos(|uy|).
    incident_angle = np.arccos(abs(uy))

    if incident_angle >= critical_angle:
        reflected_dir = np.array([ux, -uy])
        return reflected_dir / np.linalg.norm(reflected_dir)
    else:
        # Ray refracts out of the core into the cladding: signal leakage.
        return None
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-- Step 4 : Simulation Loop to Trace Light Rays Through the Fiber

def run_discrete_ray_tracing(fiber, ray, max_bounces=20):
    """Run multi bounce ray tracing inside the fiber and return the traced path."""
    path_points = [ray.pos.copy()]
    bounces = 0
    escape_detected = False

    while bounces < max_bounces:
        intersection = ray.find_exact_boundary_intersection()
        if intersection is None:
            escape_detected = True
            break

        if intersection[0] < 0 or intersection[0] > fiber.length:
            escape_detected = True
            break

        path_points.append(intersection.copy())

        reflected_dir = handle_boundary_reflection(intersection, ray.direction, fiber)
        if reflected_dir is None:
            escape_detected = True
            break

        ray.pos = intersection.copy()
        ray.direction = reflected_dir.copy()
        bounces += 1

    print(f"Ray tracing completed with {bounces} bounces. Escape detected: {escape_detected}")
    return path_points, escape_detected
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-- Step 5 : Visualization of Ray Paths Through the Fiber

def plot_ray_path(fiber, traced_points, escaped, launch_angle, case_label=""):
    fig, ax = plt.subplots(figsize=(10, 4))
    plt.title(f'2D Fiber Optic Ray Tracing Simulation - {case_label} - Launch Angle: {launch_angle:.1f}°')
    plt.xlabel("Fiber Length (microns)")
    plt.ylabel("Fiber Radius (microns)")
    plt.grid(True, color='#333333')
    ax.set_aspect('equal', adjustable='box')

    plt.xlim(-10, fiber.length + 50)
    plt.ylim(-fiber.radius - 10, fiber.radius + 10)

    L = fiber.length
    R = fiber.radius
    x_vals_fiber = [0, L]
    y_vals_upper = [R, R]
    y_vals_lower = [-R, -R]
    plt.plot(x_vals_fiber, y_vals_upper, color='white', linewidth=1)
    plt.plot(x_vals_fiber, y_vals_lower, color='white', linewidth=1)
    plt.fill_between(x_vals_fiber, y_vals_lower, y_vals_upper, color='#112233', alpha=0.8)
    plt.fill_between([0, L], R, 2*R, color='#001122', alpha=0.6)
    plt.fill_between([0, L], -2*R, -R, color='#001122', alpha=0.6)

    x_coords = [point[0] for point in traced_points]
    y_coords = [point[1] for point in traced_points]
    laser_color = '#00FFFF'
    plt.plot(x_coords, y_coords, color=laser_color, linewidth=4, alpha=0.2)
    plt.plot(x_coords, y_coords, color=laser_color, linewidth=1, alpha=1.0, marker='o', markersize=4)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#AAAAAA')
    ax.spines['bottom'].set_color('#AAAAAA')
    ax.tick_params(colors='#CCCCCC', which='both')
    ax.xaxis.label.set_color('#DDDDDD')
    ax.yaxis.label.set_color('#DDDDDD')
    ax.title.set_color('#FFFFFF')

    legend_label = 'Ray Path (Escaped)' if escaped else 'Ray Path (Confined)'
    plt.plot([], [], color=laser_color, linewidth=4, alpha=0.2, label=legend_label)
    plt.legend(loc='best', facecolor='#222222', edgecolor='#444444', labelcolor='#FFFFFF')
    print(f"Displaying {len(traced_points)} traced points of the ray path")
    plt.show()


def run_case(fiber, launch_angle, label):
    ray = Ray(pos=[0.0, 0.0], angle_deg=launch_angle, fiber=fiber)
    traced_points, escaped = run_discrete_ray_tracing(fiber, ray)
    plot_ray_path(fiber, traced_points, escaped, launch_angle, label)


def interactive_menu():
    fiber = Fiber(n_core=1.5, n_cladding=1.4, radius=30.0, length=500.0)
    critical_angle_rad = np.arcsin(fiber.n_cladding / fiber.n_core)
    critical_angle_deg = np.degrees(critical_angle_rad)
    max_launch_angle_for_TIR = 90.0 - critical_angle_deg

    presets = {
        '1': ('Strong TIR', max_launch_angle_for_TIR - 5.0),
        '2': ('Near-critical TIR', max_launch_angle_for_TIR - 0.5),
        '3': ('Leakage / escape', max_launch_angle_for_TIR + 5.0),
    }

    print('Interactive fiber simulator')
    print('Fiber core index n1=', fiber.n_core, 'cladding index n2=', fiber.n_cladding)
    print(f'Critical angle relative to normal: {critical_angle_deg:.2f}°')
    print(f'Max launch angle for TIR (relative x-axis): {max_launch_angle_for_TIR:.2f}°')
    print('Lower launch angles are closer to the fiber axis and stay trapped more easily.')

    while True:
        print('\nChoose a case:')
        for key, (label, angle) in presets.items():
            print(f'  {key}) {label} — launch angle {angle:.1f}°')
        print('  4) Custom launch angle')
        print('  q) Quit')

        choice = input('Selection: ').strip().lower()
        if choice == 'q':
            print('Exiting interactive fiber simulator.')
            break
        if choice in presets:
            label, angle = presets[choice]
            run_case(fiber, angle, label)
            continue
        if choice == '4':
            raw = input('Enter launch angle in degrees relative to x-axis: ').strip()
            try:
                angle = float(raw)
                label = f'Custom {angle:.1f}°'
                run_case(fiber, angle, label)
            except ValueError:
                print('Invalid angle input. Please enter a numeric value.')
            continue
        print('Invalid selection; please choose 1, 2, 3, 4, or q.')


def main():
    interactive_menu()


if __name__ == "__main__":
    main()



                                                                                                                                    







