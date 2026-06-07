import pygame

from settings import BULLET_DAMAGE, BULLET_RADIUS, BULLET_SPEED, SCREEN_HEIGHT, SCREEN_WIDTH, YELLOW


class Bullet:
    def __init__(
        self,
        start_pos,
        target_pos,
        damage=BULLET_DAMAGE,
        bullet_speed=BULLET_SPEED,
        spread=0,
        trail_style="pistol",
    ):
        self.pos = pygame.Vector2(start_pos)
        self.previous_pos = pygame.Vector2(start_pos)
        self.radius = BULLET_RADIUS
        self.damage = damage
        self.alive = True
        self.trail_style = trail_style

        direction = pygame.Vector2(target_pos) - self.pos
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        direction = direction.normalize().rotate(spread)
        self.velocity = direction * bullet_speed

    def update(self, dt):
        self.previous_pos.update(self.pos)
        self.pos += self.velocity * dt

        if (
            self.pos.x < -self.radius
            or self.pos.x > SCREEN_WIDTH + self.radius
            or self.pos.y < -self.radius
            or self.pos.y > SCREEN_HEIGHT + self.radius
        ):
            self.alive = False

    def draw(self, surface):
        trail_start = self.previous_pos
        trail_length = 10
        trail_width = 3
        bullet_radius = self.radius

        if self.trail_style == "smg":
            trail_length = 16
            trail_width = 2
            bullet_radius = max(3, self.radius - 1)
        elif self.trail_style == "shotgun":
            trail_length = 6
            trail_width = 2
            bullet_radius = max(3, self.radius - 1)

        trail_end = self.pos - self.velocity.normalize() * trail_length
        pygame.draw.line(surface, (255, 219, 125), trail_start, trail_end, trail_width)
        pygame.draw.circle(surface, YELLOW, self.pos, bullet_radius)
        pygame.draw.circle(surface, (255, 246, 190), self.pos, max(2, bullet_radius - 2))
