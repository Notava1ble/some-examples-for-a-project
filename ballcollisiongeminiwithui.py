import pygame
import random
import math
import sys # To exit cleanly

# Use pygame's Vector2 for easier vector math
vector2 = pygame.math.Vector2

# --- Ball Class (Unchanged from previous example) ---
class Ball:
    """
    Represents a ball with physical properties for simulation.
    """
    def __init__(self, x, y, radius, color, mass=1.0, velocity=(0, 0), acceleration=(0, 0)):
        """
        Initializes a Ball object.
        Args:
            x (float): Initial x-coordinate of the center.
            y (float): Initial y-coordinate of the center.
            radius (float): Radius of the ball.
            color (tuple): RGB color tuple (e.g., (255, 0, 0) for red).
            mass (float, optional): Mass of the ball. Defaults to 1.0.
            velocity (tuple/Vector2, optional): Initial velocity (vx, vy). Defaults to (0, 0).
            acceleration (tuple/Vector2, optional): Initial acceleration (ax, ay). Defaults to (0, 0).
        """
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
             raise TypeError("x and y must be numeric")
        if not isinstance(radius, (int, float)) or radius <= 0:
             raise ValueError("radius must be a positive number")
        # Allow zero mass for immovable objects if needed, but ensure non-negative
        if not isinstance(mass, (int, float)) or mass < 0:
             raise ValueError("mass must be a non-negative number")

        self.position = vector2(x, y)
        self.velocity = vector2(velocity)
        self.acceleration = vector2(acceleration)
        self.radius = float(radius)
        self.mass = float(mass)
        # Handle zero mass correctly for infinite mass objects
        self.inv_mass = 1.0 / self.mass if self.mass > 0 else 0
        self.color = color

    def update(self, dt):
        """
        Updates the ball's velocity and position based on its acceleration
        and the time step (dt). Uses simple Euler integration.
        Args:
            dt (float): The time step duration (in seconds).
        """
        if dt < 0:
            raise ValueError("dt cannot be negative")
        # Update velocity: v = v0 + a * dt
        self.velocity += self.acceleration * dt
        # Update position: p = p0 + v * dt
        self.position += self.velocity * dt

    def apply_force(self, force):
        """
        Applies a force to the ball, changing its acceleration (F=ma -> a=F/m).
        Args:
            force (tuple/Vector2): The force vector (fx, fy) to apply.
        """
        if self.inv_mass > 0: # Cannot apply force to object with infinite mass
             self.acceleration += vector2(force) * self.inv_mass

    def draw(self, surface):
        """
        Draws the ball onto a pygame surface.
        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        draw_pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(surface, self.color, draw_pos, int(self.radius))

    def __repr__(self):
        return (f"Ball(pos={self.position}, vel={self.velocity}, "
                f"rad={self.radius}, mass={self.mass})")

# --- UI Helper Function ---
def draw_text(surface, text, pos, font, color=pygame.Color('white')):
    """Helper to draw text on the screen."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=pos)
    surface.blit(text_surface, text_rect)
    return text_rect

def draw_input_box(surface, rect, text, font, is_active, border_color=(150, 150, 150), active_color=(255, 255, 255), text_color=(200, 200, 200)):
    """Draws an input box."""
    pygame.draw.rect(surface, active_color if is_active else border_color, rect, 2) # Border
    text_surface = font.render(text, True, text_color)
    # Position text inside the box (add some padding)
    text_rect = text_surface.get_rect(centery=rect.centery, left=rect.left + 5)
    surface.blit(text_surface, text_rect)

# --- Main Simulation Function ---
def run_simulation_with_ui():
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Collision Setup")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 200, 0)      # Defined here for UI button
    DARK_GREEN = (0, 150, 0) # Defined here for UI button hover
    GREY = (100, 100, 100)
    LIGHT_GREY = (170, 170, 170)
    INPUT_BG = (50, 50, 50)


    # Fonts
    font_small = pygame.font.Font(None, 28)
    font_medium = pygame.font.Font(None, 36)
    font_large = pygame.font.Font(None, 50)

    # --- UI State ---
    ui_active = True
    # Adjusted default velocities for more interesting ground start
    input_values = {
        "mass1": "10", "vel1x": "80", "vel1y": "-150",
        "mass2": "20", "vel2x": "-60", "vel2y": "-100",
    }
    input_rects = {}
    active_input_key = None
    error_message = ""

    # Define UI element positions and sizes
    input_width = 100
    input_height = 30
    padding = 10
    start_y_ui = 100 # Renamed to avoid conflict with simulation start_y
    col1_x = 50
    col2_x = 200
    col3_x = 450 # Ball 2 starts here
    col4_x = 600

    # Ball 1 Inputs
    input_rects["mass1"] = pygame.Rect(col2_x, start_y_ui, input_width, input_height)
    input_rects["vel1x"] = pygame.Rect(col2_x, start_y_ui + input_height + padding, input_width, input_height)
    input_rects["vel1y"] = pygame.Rect(col2_x, start_y_ui + 2 * (input_height + padding), input_width, input_height)

    # Ball 2 Inputs
    input_rects["mass2"] = pygame.Rect(col4_x, start_y_ui, input_width, input_height)
    input_rects["vel2x"] = pygame.Rect(col4_x, start_y_ui + input_height + padding, input_width, input_height)
    input_rects["vel2y"] = pygame.Rect(col4_x, start_y_ui + 2 * (input_height + padding), input_width, input_height)

    input_keys_ordered = ["mass1", "vel1x", "vel1y", "mass2", "vel2x", "vel2y"] # For TAB cycling

    # Start Button
    button_width = 200
    button_height = 50
    start_button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT - button_height - 50, button_width, button_height)

    # --- UI Loop ---
    while ui_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    # Check if start button clicked
                    if start_button_rect.collidepoint(event.pos):
                        # Try to parse values and start simulation
                        try:
                            parsed_values = {key: float(val) for key, val in input_values.items()}
                            # Basic validation
                            if parsed_values["mass1"] <= 0 or parsed_values["mass2"] <= 0:
                                raise ValueError("Mass must be positive")
                            ui_active = False # Exit UI loop successfully
                            error_message = ""
                        except ValueError:
                            error_message = "Invalid input. Please enter numbers (mass > 0)."
                            active_input_key = None # Deactivate input on error

                    # Check if an input box was clicked
                    else:
                        clicked_key = None
                        for key, rect in input_rects.items():
                            if rect.collidepoint(event.pos):
                                clicked_key = key
                                break
                        active_input_key = clicked_key
                        error_message = "" # Clear error on new interaction


            if event.type == pygame.KEYDOWN:
                if active_input_key:
                    if event.key == pygame.K_BACKSPACE:
                        input_values[active_input_key] = input_values[active_input_key][:-1]
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                         active_input_key = None # Deactivate on enter
                    elif event.key == pygame.K_TAB:
                        try:
                            current_index = input_keys_ordered.index(active_input_key)
                            next_index = (current_index + (1 if not pygame.key.get_mods() & pygame.KMOD_SHIFT else -1)) % len(input_keys_ordered) # Shift+Tab goes back
                            active_input_key = input_keys_ordered[next_index]
                        except ValueError:
                             active_input_key = input_keys_ordered[0]
                    else:
                        # Allow numbers, decimal point, and minus sign
                        current_val = input_values[active_input_key]
                        is_negative_ok = event.unicode == '-' and not current_val
                        is_decimal_ok = event.unicode == '.' and '.' not in current_val
                        if event.unicode.isdigit() or is_negative_ok or is_decimal_ok :
                             input_values[active_input_key] += event.unicode
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                     # Try starting simulation if enter pressed outside input box
                     try:
                         parsed_values = {key: float(val) for key, val in input_values.items()}
                         if parsed_values["mass1"] <= 0 or parsed_values["mass2"] <= 0:
                             raise ValueError("Mass must be positive")
                         ui_active = False
                         error_message = ""
                     except ValueError:
                         error_message = "Invalid input. Please enter numbers (mass > 0)."
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # --- Drawing UI ---
        screen.fill(BLACK)

        # Title
        draw_text(screen, "Configure Ball Properties", (WIDTH // 2 - 250, 30), font_large, WHITE)

        # Ball 1 Labels and Inputs
        draw_text(screen, "Ball 1", (col1_x, start_y_ui - 30), font_medium, RED)
        draw_text(screen, "Mass:", (col1_x, start_y_ui + 5), font_small, WHITE)
        draw_input_box(screen, input_rects["mass1"], input_values["mass1"], font_small, active_input_key == "mass1")
        draw_text(screen, "Velocity X:", (col1_x, start_y_ui + input_height + padding + 5), font_small, WHITE)
        draw_input_box(screen, input_rects["vel1x"], input_values["vel1x"], font_small, active_input_key == "vel1x")
        draw_text(screen, "Velocity Y:", (col1_x, start_y_ui + 2 * (input_height + padding) + 5), font_small, WHITE)
        draw_input_box(screen, input_rects["vel1y"], input_values["vel1y"], font_small, active_input_key == "vel1y")

        # Ball 2 Labels and Inputs
        draw_text(screen, "Ball 2", (col3_x, start_y_ui - 30), font_medium, BLUE)
        draw_text(screen, "Mass:", (col3_x, start_y_ui + 5), font_small, WHITE)
        draw_input_box(screen, input_rects["mass2"], input_values["mass2"], font_small, active_input_key == "mass2")
        draw_text(screen, "Velocity X:", (col3_x, start_y_ui + input_height + padding + 5), font_small, WHITE)
        draw_input_box(screen, input_rects["vel2x"], input_values["vel2x"], font_small, active_input_key == "vel2x")
        draw_text(screen, "Velocity Y:", (col3_x, start_y_ui + 2 * (input_height + padding) + 5), font_small, WHITE)
        draw_input_box(screen, input_rects["vel2y"], input_values["vel2y"], font_small, active_input_key == "vel2y")

        # Start Button
        mouse_pos = pygame.mouse.get_pos()
        button_color = GREEN
        if start_button_rect.collidepoint(mouse_pos):
            button_color = DARK_GREEN # Simple hover effect

        pygame.draw.rect(screen, button_color, start_button_rect)
        button_text_surf = font_medium.render("Start Simulation", True, BLACK)
        button_text_rect = button_text_surf.get_rect(center=start_button_rect.center)
        screen.blit(button_text_surf, button_text_rect)

        # Error Message
        if error_message:
            draw_text(screen, error_message, (start_button_rect.left, start_button_rect.top - 40), font_small, RED)

        pygame.display.flip()
        pygame.time.Clock().tick(30) # Limit UI refresh rate

    # --- UI finished, proceed to Simulation Setup ---
    pygame.display.set_caption("Bouncing Balls Simulation (Elastic)") # Update caption

    # Simulation parameters
    FIXED_RADIUS = 25 # Keep radius fixed for simplicity now
    GRAVITY = vector2(0, 250) # Pixels/s^2 (Increased gravity slightly for more bounce)
    RESTITUTION = 1.0 # **** Coefficient of restitution (1.0 = perfectly elastic) ****
    FRICTION = 0.001 # Reduced friction slightly for more sustained bouncing

    # Create the two balls based on UI input
    ball1_start_x = WIDTH * 0.25
    ball2_start_x = WIDTH * 0.75
    # **** Calculate start_y so balls are touching the bottom edge ****
    start_y = HEIGHT - FIXED_RADIUS -1 # Minus 1 pixel to ensure they start just above the ground

    ball1 = Ball(ball1_start_x, start_y, FIXED_RADIUS, RED,
                 mass=parsed_values["mass1"],
                 velocity=(parsed_values["vel1x"], parsed_values["vel1y"]))

    ball2 = Ball(ball2_start_x, start_y, FIXED_RADIUS, BLUE,
                 mass=parsed_values["mass2"],
                 velocity=(parsed_values["vel2x"], parsed_values["vel2y"]))

    balls = [ball1, ball2]
    collision_count = 0 # Initialize collision counter

    clock = pygame.time.Clock()
    running = True

    # --- Simulation Loop ---
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Time Step
        dt = min(clock.tick(60) / 1000.0, 0.05)

        # Physics Update
        for i, ball in enumerate(balls): # Use enumerate if you need index
            # Apply forces (Gravity, Friction)
            ball.acceleration = vector2(0, 0) # Reset acceleration each frame
            ball.apply_force(GRAVITY * ball.mass) # Gravity force = m * g
            if ball.velocity.length_squared() > 1e-6:
                 friction_force = -ball.velocity.normalize() * ball.velocity.length_squared() * FRICTION * ball.radius
                 ball.apply_force(friction_force)

            # Update state
            ball.update(dt)

            # Wall Collisions
            # Check horizontal bounds first
            if ball.position.x - ball.radius < 0:
                ball.position.x = ball.radius
                ball.velocity.x *= -RESTITUTION
            elif ball.position.x + ball.radius > WIDTH:
                ball.position.x = WIDTH - ball.radius
                ball.velocity.x *= -RESTITUTION

            # Check vertical bounds separately (Important for ground start)
            if ball.position.y - ball.radius < 0: # Top wall
                 # Prevent sticking to ceiling if restitution is exactly 1 and gravity low
                 ball.position.y = ball.radius + 1
                 ball.velocity.y *= -RESTITUTION
            elif ball.position.y + ball.radius > HEIGHT: # Bottom wall (ground)
                 # Prevent sinking through floor due to float precision / high velocity
                 ball.position.y = HEIGHT - ball.radius
                 # Only reverse velocity if moving downwards (avoids issues if starting exactly on ground)
                 if ball.velocity.y > 0:
                    ball.velocity.y *= -RESTITUTION


        # Ball-Ball Collision
        ball_a = balls[0]
        ball_b = balls[1]

        dist_vec = ball_b.position - ball_a.position
        dist_sq = dist_vec.length_squared()
        min_dist = ball_a.radius + ball_b.radius
        min_dist_sq = min_dist * min_dist

        # Check for collision (and avoid processing if perfectly overlapped, dist_sq=0)
        if 0 < dist_sq < min_dist_sq:
            distance = math.sqrt(dist_sq)
            normal = dist_vec / distance
            # tangent = vector2(-normal.y, normal.x) # Tangent not needed for this resolution

            # --- Resolve Overlap ---
            overlap = min_dist - distance
            total_inv_mass = ball_a.inv_mass + ball_b.inv_mass
            if total_inv_mass > 0: # Ensure at least one ball can move
                 # Separate balls based on inverse mass ratio
                 separation_a = normal * (overlap * ball_a.inv_mass / total_inv_mass)
                 separation_b = normal * (overlap * ball_b.inv_mass / total_inv_mass)
                 ball_a.position -= separation_a
                 ball_b.position += separation_b

            # --- Collision Response ---
            relative_velocity = ball_b.velocity - ball_a.velocity
            vel_along_normal = relative_velocity.dot(normal)

            # Only resolve if balls are moving towards each other along the normal
            if vel_along_normal < 0:
                collision_count += 1 # Increment collision counter

                # Calculate impulse scalar (j) using RESTITUTION = 1.0
                impulse_scalar = -(1 + RESTITUTION) * vel_along_normal
                impulse_scalar /= total_inv_mass # Equivalent to 1/m1 + 1/m2

                # Apply impulse along the normal
                impulse_vec = normal * impulse_scalar

                ball_a.velocity -= impulse_vec * ball_a.inv_mass
                ball_b.velocity += impulse_vec * ball_b.inv_mass


        # Drawing
        screen.fill(BLACK)
        for ball in balls:
            ball.draw(screen)

        # Draw Collision Counter
        draw_text(screen, f"Collisions: {collision_count}", (10, 10), font_medium, WHITE)

        pygame.display.flip()

    pygame.quit()
    sys.exit() # Exit cleanly

# --- Run the main function ---
if __name__ == "__main__":
     run_simulation_with_ui()