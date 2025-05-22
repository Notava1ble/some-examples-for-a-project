import pygame
import random
import math

# Use pygame's Vector2 for easier vector math
vector2 = pygame.math.Vector2

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
        if not isinstance(mass, (int, float)) or mass <= 0:
             raise ValueError("mass must be a positive number")

        self.position = vector2(x, y)
        self.velocity = vector2(velocity)
        self.acceleration = vector2(acceleration)
        self.radius = float(radius)
        self.mass = float(mass)
        self.inv_mass = 1.0 / self.mass if self.mass > 0 else 0 # Precompute inverse mass for efficiency
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
        # Pygame's draw.circle expects integer coordinates for the center
        draw_pos = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(surface, self.color, draw_pos, int(self.radius))

    def __repr__(self):
        return (f"Ball(pos={self.position}, vel={self.velocity}, "
                f"rad={self.radius}, mass={self.mass})")

# --- End of Ball Class ---

# --- Pygame Simulation Example ---

def run_collision_simulation():
    """
    Runs a Pygame simulation demonstrating Ball collisions.
    """
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Balls Simulation")

    # Colors
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    BLACK = (0, 0, 0)
    COLORS = [RED, GREEN, BLUE, YELLOW, (255, 165, 0), (128, 0, 128)]

    # Simulation parameters
    NUM_BALLS = 15
    MIN_RADIUS = 10
    MAX_RADIUS = 25
    MAX_INITIAL_SPEED = 150 # pixels per second
    GRAVITY = vector2(0, 250) # Pixels/s^2 - Simulates gravity pulling down
    RESTITUTION = 0.85 # Coefficient of restitution (bounciness, 0=inelastic, 1=perfectly elastic)
    FRICTION = 0.005 # Simple velocity dampening factor per frame

    balls = []
    for _ in range(NUM_BALLS):
        radius = random.uniform(MIN_RADIUS, MAX_RADIUS)
        # Ensure balls don't start overlapping screen edges
        x = random.uniform(radius, WIDTH - radius)
        y = random.uniform(radius, HEIGHT - radius)
        color = random.choice(COLORS)
        # Assign mass proportional to area (pi*r^2), density assumed constant
        mass = math.pi * radius**2
        vx = random.uniform(-MAX_INITIAL_SPEED, MAX_INITIAL_SPEED)
        vy = random.uniform(-MAX_INITIAL_SPEED, MAX_INITIAL_SPEED)

        # Create the ball BUT set acceleration to ZERO initially.
        # We'll apply gravity each frame if desired.
        ball = Ball(x, y, radius, color, mass=mass, velocity=(vx, vy), acceleration=(0, 0))
        balls.append(ball)


    clock = pygame.time.Clock()
    running = True

    # --- Dragging State ---
    dragging_ball = None
    drag_offset = vector2(0, 0)
    last_mouse_pos = None

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                     running = False
            # --- Mouse Dragging Events ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = vector2(event.pos)
                for ball in balls:
                    if (mouse_pos - ball.position).length() <= ball.radius:
                        dragging_ball = ball
                        drag_offset = ball.position - mouse_pos
                        last_mouse_pos = mouse_pos
                        ball.velocity = vector2(0, 0)
                        break
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_ball is not None and last_mouse_pos is not None:
                    mouse_pos = vector2(event.pos)
                    drag_velocity = (mouse_pos - last_mouse_pos) / max(dt, 1e-6)
                    dragging_ball.velocity = drag_velocity
                dragging_ball = None
                last_mouse_pos = None
            if event.type == pygame.MOUSEMOTION:
                if dragging_ball is not None:
                    mouse_pos = vector2(event.pos)
                    dragging_ball.position = mouse_pos + drag_offset
                    last_mouse_pos = mouse_pos

        # --- Time Step ---
        dt = min(clock.tick(60) / 1000.0, 0.05) # Max dt of 0.05s (equiv to 20 FPS min)

        # --- Physics Update ---
        for i, ball in enumerate(balls):
            # Skip physics for dragged ball
            if ball is dragging_ball:
                continue
            # 1. Apply forces (like gravity) - Reset acceleration first if forces are frame-dependent
            ball.acceleration = vector2(0, 0) # Reset acceleration if forces change each frame
            ball.apply_force(GRAVITY * ball.mass) # Gravity force = m * g

            # Apply simple friction/air resistance
            if ball.velocity.length_squared() > 0: # Avoid applying friction to stationary balls
                 friction_force = -ball.velocity.normalize() * ball.velocity.length_squared() * FRICTION
                 ball.apply_force(friction_force)

            # 2. Update position and velocity
            ball.update(dt)

            # 3. Handle Wall Collisions
            if ball.position.x - ball.radius < 0: # Left wall
                ball.position.x = ball.radius # Clamp position
                ball.velocity.x *= -RESTITUTION
            elif ball.position.x + ball.radius > WIDTH: # Right wall
                ball.position.x = WIDTH - ball.radius # Clamp position
                ball.velocity.x *= -RESTITUTION

            if ball.position.y - ball.radius < 0: # Top wall
                ball.position.y = ball.radius # Clamp position
                ball.velocity.y *= -RESTITUTION
            elif ball.position.y + ball.radius > HEIGHT: # Bottom wall
                ball.position.y = HEIGHT - ball.radius # Clamp position
                ball.velocity.y *= -RESTITUTION


        # 4. Handle Ball-Ball Collisions (Check every pair)
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)): # Avoid self-collision and double checks
                ball_a = balls[i]
                ball_b = balls[j]

                dist_vec = ball_b.position - ball_a.position
                dist_sq = dist_vec.length_squared()
                min_dist = ball_a.radius + ball_b.radius
                min_dist_sq = min_dist * min_dist

                if dist_sq < min_dist_sq and dist_sq > 1e-6: # Check for collision and avoid division by zero if perfectly overlapped
                    distance = math.sqrt(dist_sq)
                    normal = dist_vec / distance # Normalized collision normal (vector from A to B)
                    tangent = vector2(-normal.y, normal.x) # Collision tangent

                    # --- Resolve Overlap ---
                    # Move balls apart so they are just touching
                    overlap = min_dist - distance
                    # Move them based on inverse mass (lighter balls move more)
                    total_inv_mass = ball_a.inv_mass + ball_b.inv_mass
                    if total_inv_mass == 0: continue # Both have infinite mass - shouldn't happen here

                    separation_a = normal * (overlap * ball_a.inv_mass / total_inv_mass)
                    separation_b = normal * (overlap * ball_b.inv_mass / total_inv_mass)
                    ball_a.position -= separation_a
                    ball_b.position += separation_b


                    # --- Collision Response (Elastic Collision Physics) ---
                    # Relative velocity
                    relative_velocity = ball_b.velocity - ball_a.velocity
                    # Relative velocity along the normal
                    vel_along_normal = relative_velocity.dot(normal)

                    # Only resolve collision if balls are moving towards each other
                    if vel_along_normal < 0:
                        # Calculate impulse scalar (j)
                        impulse_scalar = -(1 + RESTITUTION) * vel_along_normal
                        impulse_scalar /= total_inv_mass # Equivalent to 1/m1 + 1/m2

                        # Apply impulse along the normal
                        impulse_vec = normal * impulse_scalar

                        ball_a.velocity -= impulse_vec * ball_a.inv_mass
                        ball_b.velocity += impulse_vec * ball_b.inv_mass


        # --- Drawing ---
        screen.fill(BLACK) # Clear screen

        for ball in balls:
            ball.draw(screen) # Draw each ball

        pygame.display.flip() # Update the full display surface

    pygame.quit()

# Run the simulation if the script is executed directly
if __name__ == "__main__":
    run_collision_simulation()