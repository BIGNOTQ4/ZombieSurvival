import random

from settings import (
    DEBUG_MODE,
    FIRST_WAVE_ZOMBIES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPAWN_DELAY,
    WAVE_BREAK_TIME,
    ZOMBIES_PER_WAVE_INCREASE,
)
from zombie import Zombie


class WaveManager:
    def __init__(self, difficulty_config=None):
        self.difficulty_config = difficulty_config or {
            "health": 1.0,
            "speed": 1.0,
            "spawn_count": 1.0,
        }
        self.wave = 0
        self.zombies_to_spawn = 0
        self.spawned_this_wave = 0
        self.spawn_timer = 0
        self.wave_break_timer = 0
        self.wave_completed = False
        self.upgrade_ready = False
        self.is_boss_wave = False

    def reset(self):
        self.wave = 0
        self.zombies_to_spawn = 0
        self.spawned_this_wave = 0
        self.spawn_timer = 0
        self.wave_break_timer = 0
        self.wave_completed = False
        self.upgrade_ready = False
        self.is_boss_wave = False

    def update(self, dt, zombies):
        if self.wave_completed:
            self.wave_break_timer += dt * 1000
            if self.wave_break_timer >= WAVE_BREAK_TIME:
                self.upgrade_ready = True
            return

        if self.spawned_this_wave < self.zombies_to_spawn:
            self.spawn_timer += dt * 1000

            if self.spawn_timer >= SPAWN_DELAY:
                spawn_pos = self.get_edge_spawn_position()
                zombie_type = self.choose_zombie_type()
                zombies.append(Zombie(spawn_pos, self.wave, zombie_type, self.difficulty_config))
                self.spawned_this_wave += 1
                self.spawn_timer = 0
                if DEBUG_MODE:
                    print(f"Spawned {zombie_type} zombie {self.spawned_this_wave}/{self.zombies_to_spawn} at {spawn_pos}")

        if self.zombies_to_spawn > 0 and self.spawned_this_wave == self.zombies_to_spawn and not zombies:
            self.zombies_to_spawn = 0
            self.wave_break_timer = 0
            self.wave_completed = True
            self.upgrade_ready = False

    def start_next_wave(self):
        self.wave += 1
        self.is_boss_wave = self.wave % 5 == 0
        if self.is_boss_wave:
            normal_escorts = min(4, 1 + self.wave // 5)
            self.zombies_to_spawn = 1 + normal_escorts
        else:
            base_count = FIRST_WAVE_ZOMBIES + (self.wave - 1) * ZOMBIES_PER_WAVE_INCREASE
            self.zombies_to_spawn = max(1, int(base_count * self.difficulty_config["spawn_count"]))
        self.spawned_this_wave = 0
        self.spawn_timer = SPAWN_DELAY
        self.wave_break_timer = 0
        self.wave_completed = False
        self.upgrade_ready = False

    def choose_zombie_type(self):
        if self.is_boss_wave:
            if self.spawned_this_wave == 0:
                return "boss"
            return "normal"

        roll = random.random()

        if self.wave >= 4:
            tank_chance = min(0.08 + (self.wave - 4) * 0.03, 0.22)
            fast_chance = min(0.25 + (self.wave - 3) * 0.04, 0.45)

            if roll < tank_chance:
                return "tank"
            if roll < tank_chance + fast_chance:
                return "fast"

        if self.wave >= 3:
            fast_chance = min(0.25 + (self.wave - 3) * 0.05, 0.5)
            if roll < fast_chance:
                return "fast"

        return "normal"

    def get_edge_spawn_position(self):
        side = random.choice(("top", "right", "bottom", "left"))
        padding = 40

        if side == "top":
            return random.randint(0, SCREEN_WIDTH), -padding
        if side == "right":
            return SCREEN_WIDTH + padding, random.randint(0, SCREEN_HEIGHT)
        if side == "bottom":
            return random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + padding
        return -padding, random.randint(0, SCREEN_HEIGHT)
