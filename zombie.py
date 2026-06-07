import pygame

from settings import (
    BLOOD_DARK,
    GREEN,
    RED,
    RED_DARK,
    WHITE,
    YELLOW,
    ZOMBIE_DAMAGE,
    ZOMBIE_GREEN,
    ZOMBIE_GREEN_DARK,
    ZOMBIE_HEALTH,
    ZOMBIE_RADIUS,
    ZOMBIE_SPEED,
)


class Zombie:
    def __init__(self, pos, wave, zombie_type="normal", difficulty_config=None):
        self.pos = pygame.Vector2(pos)
        self.zombie_type = zombie_type
        self.difficulty_config = difficulty_config or {"health": 1.0, "speed": 1.0}
        self.setup_stats(wave)
        self.health = self.max_health
        self.alive = True
        self.facing = pygame.Vector2(1, 0)
        self.charge_cooldown = 3.5
        self.charge_timer = 1.5
        self.charge_warning_time = 0.65
        self.charge_warning_timer = 0
        self.charge_time = 0
        self.charge_direction = pygame.Vector2(1, 0)

    def setup_stats(self, wave):
        speed_bonus = min(wave * 3, 55)
        health_bonus = wave * 6

        if self.zombie_type == "fast":
            self.radius = ZOMBIE_RADIUS - 5
            self.speed = ZOMBIE_SPEED + 70 + speed_bonus
            self.max_health = ZOMBIE_HEALTH - 25 + health_bonus
            self.damage = ZOMBIE_DAMAGE
            self.score_value = 15
            self.body_color = (118, 210, 95)
            self.outline_color = (47, 118, 55)
        elif self.zombie_type == "tank":
            self.radius = ZOMBIE_RADIUS + 10
            self.speed = ZOMBIE_SPEED - 25 + speed_bonus
            self.max_health = ZOMBIE_HEALTH + 130 + health_bonus * 2
            self.damage = ZOMBIE_DAMAGE + 8
            self.score_value = 35
            self.body_color = (54, 104, 62)
            self.outline_color = (24, 54, 34)
        elif self.zombie_type == "boss":
            boss_level = max(1, wave // 5)
            self.radius = ZOMBIE_RADIUS + 28
            self.speed = ZOMBIE_SPEED - 10 + min(wave * 2, 35)
            self.max_health = 650 + boss_level * 260
            self.damage = ZOMBIE_DAMAGE + 18 + boss_level * 3
            self.score_value = 250 + boss_level * 100
            self.body_color = (92, 42, 78)
            self.outline_color = (42, 20, 44)
        else:
            self.radius = ZOMBIE_RADIUS
            self.speed = ZOMBIE_SPEED + speed_bonus
            self.max_health = ZOMBIE_HEALTH + health_bonus
            self.damage = ZOMBIE_DAMAGE
            self.score_value = 10
            self.body_color = ZOMBIE_GREEN
            self.outline_color = ZOMBIE_GREEN_DARK

        self.max_health = int(self.max_health * self.difficulty_config["health"])
        self.speed *= self.difficulty_config["speed"]

    def update(self, dt, player_pos):
        direction = pygame.Vector2(player_pos) - self.pos
        if direction.length_squared() > 0:
            self.facing = direction.normalize()

        if self.zombie_type == "boss":
            self.update_boss_movement(dt)
        else:
            self.pos += self.facing * self.speed * dt

    def update_boss_movement(self, dt):
        if self.charge_time > 0:
            self.pos += self.charge_direction * self.speed * 3.4 * dt
            self.charge_time -= dt
            return

        if self.charge_warning_timer > 0:
            self.charge_warning_timer -= dt
            self.pos += self.facing * self.speed * 0.35 * dt
            if self.charge_warning_timer <= 0:
                self.charge_direction = pygame.Vector2(self.facing)
                self.charge_time = 0.38
                self.charge_timer = self.charge_cooldown
            return

        self.charge_timer -= dt
        if self.charge_timer <= 0:
            self.charge_warning_timer = self.charge_warning_time
            return

        self.pos += self.facing * self.speed * dt

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def draw(self, surface):
        shadow_pos = self.pos + pygame.Vector2(4, 6)
        pygame.draw.circle(surface, (5, 7, 10), shadow_pos, self.radius + 5)
        pygame.draw.circle(surface, self.outline_color, self.pos, self.radius + 4)
        pygame.draw.circle(surface, self.body_color, self.pos, self.radius)

        if self.zombie_type == "fast":
            streak_start = self.pos - self.facing * (self.radius + 7)
            streak_end = self.pos - self.facing * 4
            pygame.draw.line(surface, GREEN, streak_start, streak_end, 3)
        elif self.zombie_type == "tank":
            plate_rect = pygame.Rect(0, 0, self.radius + 12, 8)
            plate_rect.center = self.pos - self.facing * 2
            pygame.draw.rect(surface, (33, 65, 42), plate_rect, border_radius=4)
        elif self.zombie_type == "boss":
            horn_side = pygame.Vector2(-self.facing.y, self.facing.x)
            left_horn = self.pos + self.facing * 18 + horn_side * 25
            right_horn = self.pos + self.facing * 18 - horn_side * 25
            pygame.draw.circle(surface, RED_DARK, left_horn, 9)
            pygame.draw.circle(surface, RED_DARK, right_horn, 9)
            pygame.draw.circle(surface, RED, self.pos - self.facing * 9, self.radius - 16)

            if self.charge_warning_timer > 0:
                end_pos = self.pos + self.facing * 130
                pygame.draw.line(surface, (255, 80, 80), self.pos, end_pos, 5)
                pygame.draw.circle(surface, (255, 120, 80), self.pos, self.radius + 9, width=3)

        eye_side = pygame.Vector2(-self.facing.y, self.facing.x)
        eye_center = self.pos + self.facing * 7
        left_eye = eye_center + eye_side * 7
        right_eye = eye_center - eye_side * 7
        pygame.draw.circle(surface, WHITE, left_eye, 4)
        pygame.draw.circle(surface, WHITE, right_eye, 4)
        pygame.draw.circle(surface, BLOOD_DARK, left_eye, 2)
        pygame.draw.circle(surface, BLOOD_DARK, right_eye, 2)

        if self.health == self.max_health:
            return

        bar_width = self.radius * 2 + 8
        health_ratio = max(0, self.health / self.max_health)
        bar_rect = pygame.Rect(0, 0, bar_width, 5)
        bar_rect.center = (self.pos.x, self.pos.y - self.radius - 12)

        pygame.draw.rect(surface, RED_DARK, bar_rect, border_radius=3)
        fill_rect = bar_rect.copy()
        fill_rect.width = int(bar_width * health_ratio)
        pygame.draw.rect(surface, YELLOW if health_ratio < 0.45 else GREEN, fill_rect, border_radius=3)
