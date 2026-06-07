import math

import pygame

from settings import (
    ACCENT,
    ACCENT_DARK,
    BLACK,
    PANEL_LIGHT,
    PLAYER_HIT_COOLDOWN,
    PLAYER_MAX_HEALTH,
    PLAYER_RADIUS,
    PLAYER_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)


class Player:
    def __init__(self):
        self.pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.radius = PLAYER_RADIUS
        self.speed = PLAYER_SPEED
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.last_hit_time = -PLAYER_HIT_COOLDOWN

    def reset(self):
        self.pos.update(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.speed = PLAYER_SPEED
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.last_hit_time = -PLAYER_HIT_COOLDOWN

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed * dt
        self.pos.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(SCREEN_HEIGHT - self.radius, self.pos.y))

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if now - self.last_hit_time < PLAYER_HIT_COOLDOWN:
            return False

        self.health = max(0, self.health - amount)
        self.last_hit_time = now
        return True

    def draw(self, surface):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        aim = mouse_pos - self.pos
        angle = math.atan2(aim.y, aim.x) if aim.length_squared() > 0 else 0
        aim_direction = pygame.Vector2(math.cos(angle), math.sin(angle))
        side_direction = pygame.Vector2(-aim_direction.y, aim_direction.x)

        shadow_pos = self.pos + pygame.Vector2(4, 6)
        pygame.draw.circle(surface, (5, 7, 10), shadow_pos, self.radius + 5)

        pygame.draw.circle(surface, ACCENT_DARK, self.pos, self.radius + 4)
        pygame.draw.circle(surface, ACCENT, self.pos, self.radius)
        pygame.draw.circle(surface, PANEL_LIGHT, self.pos - aim_direction * 5, self.radius - 8)

        nose = self.pos + aim_direction * (self.radius + 5)
        left = self.pos - aim_direction * 2 + side_direction * 9
        right = self.pos - aim_direction * 2 - side_direction * 9
        pygame.draw.polygon(surface, WHITE, (nose, left, right))

        barrel_start = self.pos + aim_direction * 13 + side_direction * 5
        barrel_end = self.pos + aim_direction * 40 + side_direction * 5
        pygame.draw.line(surface, BLACK, barrel_start, barrel_end, 9)
        pygame.draw.line(surface, WHITE, barrel_start, barrel_end, 5)
        pygame.draw.circle(surface, BLACK, barrel_end, 5)
