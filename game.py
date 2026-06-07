import json
import random
import sys
from pathlib import Path

import pygame

from bullet import Bullet
from player import Player
from settings import (
    BG_COLOR,
    BLOOD,
    BLOOD_DARK,
    BOOST_DURATION,
    DEBUG_MODE,
    BULLET_SPEED,
    FPS,
    HIT_PARTICLE_COUNT,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    POWERUP_DROP_CHANCE,
    POWERUP_LIFETIME,
    RED,
    SCREEN_HEIGHT,
    SCREEN_SHAKE_STRENGTH,
    SCREEN_SHAKE_TIME,
    SCREEN_WIDTH,
    YELLOW,
)
from ui import UI
from wave_manager import WaveManager


class HitParticle:
    def __init__(self, pos, color=None):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.velocity.length_squared() == 0:
            self.velocity = pygame.Vector2(1, 0)
        self.velocity = self.velocity.normalize() * random.randint(90, 220)
        self.radius = random.randint(4, 8)
        self.life = random.uniform(0.28, 0.55)
        self.max_life = self.life
        self.color = color or random.choice((BLOOD, BLOOD_DARK, RED))

    def update(self, dt):
        self.pos += self.velocity * dt
        self.velocity *= 0.88
        self.life -= dt

    def draw(self, surface):
        alpha_ratio = max(0, self.life / self.max_life)
        particle_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
        alpha = int(230 * alpha_ratio)
        center = (self.radius * 3 // 2, self.radius * 3 // 2)
        pygame.draw.circle(particle_surface, (*self.color, alpha), center, int(self.radius * alpha_ratio) + 1)
        surface.blit(particle_surface, (self.pos.x - center[0], self.pos.y - center[1]))

    def is_alive(self):
        return self.life > 0


class PowerUp:
    TYPES = {
        "health": {"name": "Health Pack", "label": "+", "color": (75, 220, 125)},
        "ammo": {"name": "Ammo Pack", "label": "A", "color": (245, 190, 75)},
        "rapid": {"name": "Rapid Fire", "label": "R", "color": (88, 166, 255)},
        "damage": {"name": "Damage Boost", "label": "D", "color": (235, 86, 86)},
        "speed": {"name": "Speed Boost", "label": "S", "color": (170, 115, 255)},
    }

    def __init__(self, pos, powerup_type):
        self.pos = pygame.Vector2(pos)
        self.powerup_type = powerup_type
        self.radius = 18
        self.life = POWERUP_LIFETIME
        self.alive = True

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, font):
        data = self.TYPES[self.powerup_type]
        pulse = 1 + 0.12 * abs(pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() * 0.18).y)
        glow_radius = int((self.radius + 9) * pulse)

        glow = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*data["color"], 55), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow, (self.pos.x - glow_radius, self.pos.y - glow_radius))

        pygame.draw.circle(surface, (7, 10, 15), self.pos + pygame.Vector2(3, 5), self.radius + 3)
        pygame.draw.circle(surface, data["color"], self.pos, self.radius)
        pygame.draw.circle(surface, (245, 247, 250), self.pos, self.radius, width=2)

        label = font.render(data["label"], True, (12, 14, 18))
        label_rect = label.get_rect(center=self.pos)
        surface.blit(label, label_rect)

    def collides_with_player(self, player):
        return self.pos.distance_to(player.pos) <= self.radius + player.radius


class SoundManager:
    def __init__(self, settings_data):
        self.settings_data = settings_data
        self.sounds = {}
        self.enabled = False

        try:
            pygame.mixer.init()
            self.enabled = True
            self.load_sounds()
            self.apply_settings(settings_data)
        except pygame.error:
            self.enabled = False

    def load_sounds(self):
        sound_files = {
            "shoot": "sounds/shoot.wav",
            "reload": "sounds/reload.wav",
            "zombie_hit": "sounds/zombie_hit.wav",
            "zombie_death": "sounds/zombie_death.wav",
            "powerup": "sounds/powerup.wav",
            "boss_wave": "sounds/boss_wave.wav",
            "player_damage": "sounds/player_damage.wav",
        }

        for name, path in sound_files.items():
            try:
                sound_path = Game.get_app_directory() / path
                self.sounds[name] = pygame.mixer.Sound(str(sound_path))
            except (pygame.error, FileNotFoundError, OSError):
                pass

    def apply_settings(self, settings_data):
        self.settings_data = settings_data
        if not self.enabled:
            return

        volume = settings_data["master_volume"]
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def play(self, name):
        if not self.enabled or not self.settings_data["sound_effects"]:
            return

        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()


class Game:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    UPGRADE = "upgrade"
    SETTINGS = "settings"
    CONTROLS = "controls"
    GAME_OVER = "game_over"
    DEFAULT_SETTINGS = {
        "master_volume": 0.7,
        "sound_effects": True,
        "show_controls": True,
        "difficulty": "Normal",
    }
    DIFFICULTY_CONFIGS = {
        "Easy": {"health": 0.8, "speed": 0.9, "spawn_count": 0.8, "drop_chance": 1.35},
        "Normal": {"health": 1.0, "speed": 1.0, "spawn_count": 1.0, "drop_chance": 1.0},
        "Hard": {"health": 1.25, "speed": 1.12, "spawn_count": 1.25, "drop_chance": 0.75},
    }

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = self.MENU
        self.previous_state = self.MENU
        self.settings_data = self.load_settings()
        self.sound_manager = SoundManager(self.settings_data)

        self.ui = UI()
        self.player = Player()
        self.wave_manager = None
        self.bullets = []
        self.zombies = []
        self.particles = []
        self.powerups = []
        self.weapons = self.create_weapons()
        self.current_weapon_key = "pistol"
        self.weapon_ammo = {}
        self.score = 0
        self.last_shot_time = 0
        self.damage_bonus = 0
        self.magazine_bonus = 0
        self.reload_bonus = 0
        self.reloading = False
        self.reload_timer = 0
        self.shake_timer = 0
        self.upgrade_choices = []
        self.active_boosts = {}
        self.boss_wave_text_timer = 0
        self.high_score = self.load_high_score()
        self.zombies_killed = 0
        self.debug_font = pygame.font.Font(None, 24)
        self.powerup_font = pygame.font.Font(None, 24)

    def create_weapons(self):
        return {
            "pistol": {
                "name": "Pistol",
                "damage": 35,
                "cooldown": 180,
                "magazine_size": 12,
                "reload_time": 1200,
                "bullet_speed": BULLET_SPEED,
                "bullet_count": 1,
                "spread": 2,
                "trail_style": "pistol",
            },
            "smg": {
                "name": "SMG",
                "damage": 20,
                "cooldown": 75,
                "magazine_size": 24,
                "reload_time": 1450,
                "bullet_speed": BULLET_SPEED + 80,
                "bullet_count": 1,
                "spread": 9,
                "trail_style": "smg",
            },
            "shotgun": {
                "name": "Shotgun",
                "damage": 24,
                "cooldown": 650,
                "magazine_size": 6,
                "reload_time": 1700,
                "bullet_speed": BULLET_SPEED - 90,
                "bullet_count": 6,
                "spread": 24,
                "trail_style": "shotgun",
            },
        }

    @staticmethod
    def get_app_directory():
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent

    def get_save_path(self, filename):
        return self.get_app_directory() / filename

    def load_high_score(self):
        high_score_path = self.get_save_path("high_score.json")
        try:
            with open(high_score_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return int(data.get("high_score", 0))
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
            self.create_default_high_score()
            return 0

    def create_default_high_score(self):
        try:
            with open(self.get_save_path("high_score.json"), "w", encoding="utf-8") as file:
                json.dump({"high_score": 0}, file, indent=2)
        except OSError:
            pass

    def save_high_score(self):
        if self.score <= self.high_score:
            return

        self.high_score = self.score
        try:
            with open(self.get_save_path("high_score.json"), "w", encoding="utf-8") as file:
                json.dump({"high_score": self.high_score}, file, indent=2)
        except OSError:
            pass

    def load_settings(self):
        settings_path = self.get_save_path("settings.json")
        try:
            with open(settings_path, "r", encoding="utf-8") as file:
                saved_settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            settings_data = dict(self.DEFAULT_SETTINGS)
            self.save_settings_data(settings_data)
            return settings_data

        settings_data = dict(self.DEFAULT_SETTINGS)
        settings_data.update(saved_settings)

        if settings_data["difficulty"] not in self.DIFFICULTY_CONFIGS:
            settings_data["difficulty"] = "Normal"
        try:
            settings_data["master_volume"] = max(0.0, min(1.0, float(settings_data["master_volume"])))
        except (TypeError, ValueError):
            settings_data["master_volume"] = self.DEFAULT_SETTINGS["master_volume"]
        settings_data["sound_effects"] = bool(settings_data["sound_effects"])
        settings_data["show_controls"] = bool(settings_data["show_controls"])
        self.save_settings_data(settings_data)
        return settings_data

    def save_settings(self):
        self.save_settings_data(self.settings_data)

    def save_settings_data(self, settings_data):
        try:
            with open(self.get_save_path("settings.json"), "w", encoding="utf-8") as file:
                json.dump(settings_data, file, indent=2)
        except OSError:
            pass

    def get_difficulty_config(self):
        return self.DIFFICULTY_CONFIGS[self.settings_data["difficulty"]]

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()

            if self.state == self.PLAYING:
                self.update(dt)

            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            event_state = self.state

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if event_state == self.SETTINGS:
                    self.state = self.MENU
                elif event_state == self.CONTROLS:
                    self.state = self.previous_state
                else:
                    self.toggle_pause()

            if event_state == self.MENU and self.ui.start_button.is_clicked(event):
                self.start_game()

            if event_state == self.MENU and self.ui.settings_button.is_clicked(event):
                self.state = self.SETTINGS

            if event_state == self.MENU and self.ui.controls_button.is_clicked(event):
                self.previous_state = self.MENU
                self.state = self.CONTROLS

            if event_state == self.GAME_OVER and self.ui.restart_button.is_clicked(event):
                self.start_game()

            if event_state == self.GAME_OVER and self.ui.game_over_menu_button.is_clicked(event):
                self.return_to_menu()

            if event_state == self.SETTINGS and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_settings_click(event.pos)

            if event_state == self.CONTROLS and self.ui.back_button.is_clicked(event):
                self.state = self.previous_state

            if event_state == self.PAUSED and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.ui.resume_button.rect.collidepoint(event.pos):
                    self.state = self.PLAYING
                elif self.ui.pause_controls_button.rect.collidepoint(event.pos):
                    self.previous_state = self.PAUSED
                    self.state = self.CONTROLS
                elif self.ui.main_menu_button.rect.collidepoint(event.pos):
                    self.return_to_menu()

            if event_state == self.UPGRADE and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.choose_upgrade(event.pos)

            if event_state == self.PLAYING and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.start_reload()
                elif event.key == pygame.K_1:
                    self.switch_weapon("pistol")
                elif event.key == pygame.K_2:
                    self.switch_weapon("smg")
                elif event.key == pygame.K_3:
                    self.switch_weapon("shotgun")

            if event_state == self.PLAYING and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.shoot()

    def toggle_pause(self):
        if self.state == self.PLAYING:
            self.state = self.PAUSED
        elif self.state == self.PAUSED:
            self.state = self.PLAYING

    def return_to_menu(self):
        self.state = self.MENU
        self.bullets.clear()
        self.zombies.clear()
        self.particles.clear()
        self.powerups.clear()
        self.reloading = False
        self.active_boosts = {}

    def handle_settings_click(self, mouse_pos):
        if self.ui.back_button.rect.collidepoint(mouse_pos):
            self.save_settings()
            self.state = self.MENU
            return

        if self.ui.volume_down_button.rect.collidepoint(mouse_pos):
            self.settings_data["master_volume"] = max(0.0, self.settings_data["master_volume"] - 0.1)
        elif self.ui.volume_up_button.rect.collidepoint(mouse_pos):
            self.settings_data["master_volume"] = min(1.0, self.settings_data["master_volume"] + 0.1)
        elif self.ui.sfx_button.rect.collidepoint(mouse_pos):
            self.settings_data["sound_effects"] = not self.settings_data["sound_effects"]
        elif self.ui.help_button.rect.collidepoint(mouse_pos):
            self.settings_data["show_controls"] = not self.settings_data["show_controls"]
        else:
            for difficulty, button in self.ui.difficulty_buttons.items():
                if button.rect.collidepoint(mouse_pos):
                    self.settings_data["difficulty"] = difficulty

        self.sound_manager.apply_settings(self.settings_data)
        self.save_settings()

    def start_game(self):
        self.state = self.PLAYING
        self.player.reset()
        self.wave_manager = WaveManager(self.get_difficulty_config())
        self.start_next_wave()
        self.bullets.clear()
        self.zombies.clear()
        self.particles.clear()
        self.powerups.clear()
        self.score = 0
        self.last_shot_time = 0
        self.current_weapon_key = "pistol"
        self.damage_bonus = 0
        self.magazine_bonus = 0
        self.reload_bonus = 0
        self.weapon_ammo = {
            weapon_key: weapon["magazine_size"]
            for weapon_key, weapon in self.weapons.items()
        }
        self.reloading = False
        self.reload_timer = 0
        self.shake_timer = 0
        self.upgrade_choices = []
        self.active_boosts = {}
        self.boss_wave_text_timer = 0
        self.zombies_killed = 0

    def start_next_wave(self):
        self.wave_manager.start_next_wave()
        if self.wave_manager.is_boss_wave:
            self.boss_wave_text_timer = 2.4
            self.sound_manager.play("boss_wave")

    def switch_weapon(self, weapon_key):
        if weapon_key == self.current_weapon_key:
            return

        self.current_weapon_key = weapon_key
        self.reloading = False
        self.reload_timer = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        weapon = self.get_current_weapon()
        if self.reloading or now - self.last_shot_time < self.get_current_cooldown(weapon):
            return

        if self.get_current_ammo() <= 0:
            self.start_reload()
            return

        self.fire_weapon(weapon)
        self.weapon_ammo[self.current_weapon_key] -= 1
        self.last_shot_time = now
        self.sound_manager.play("shoot")

        if self.get_current_ammo() == 0:
            self.start_reload()

    def fire_weapon(self, weapon):
        spread = weapon["spread"]
        bullet_count = weapon["bullet_count"]

        for pellet_index in range(bullet_count):
            if bullet_count == 1:
                pellet_spread = random.uniform(-spread, spread)
            else:
                spacing = spread / max(1, bullet_count - 1)
                pellet_spread = -spread / 2 + pellet_index * spacing
                pellet_spread += random.uniform(-3, 3)

            self.bullets.append(
                Bullet(
                    self.player.pos,
                    pygame.mouse.get_pos(),
                    self.get_weapon_damage(weapon),
                    weapon["bullet_speed"],
                    pellet_spread,
                    weapon["trail_style"],
                )
            )

    def start_reload(self):
        if self.reloading or self.get_current_ammo() == self.get_current_magazine_size():
            return

        self.reloading = True
        self.reload_timer = 0
        self.sound_manager.play("reload")

    def get_current_weapon(self):
        return self.weapons[self.current_weapon_key]

    def get_current_weapon_name(self):
        return self.get_current_weapon()["name"]

    def get_current_ammo(self):
        return self.weapon_ammo.get(self.current_weapon_key, 0)

    def get_current_magazine_size(self):
        return self.get_current_weapon()["magazine_size"] + self.magazine_bonus

    def get_current_reload_time(self):
        return max(500, self.get_current_weapon()["reload_time"] - self.reload_bonus)

    def get_weapon_damage(self, weapon):
        damage = weapon["damage"] + self.damage_bonus
        if "damage" in self.active_boosts:
            damage += 15
        return damage

    def get_current_cooldown(self, weapon):
        cooldown = weapon["cooldown"]
        if "rapid" in self.active_boosts:
            cooldown *= 0.55
        return cooldown

    def update(self, dt):
        self.update_boosts(dt)
        self.update_reloading(dt)
        self.boss_wave_text_timer = max(0, self.boss_wave_text_timer - dt)
        self.shake_timer = max(0, self.shake_timer - dt * 1000)
        self.player.update(dt)
        self.wave_manager.update(dt, self.zombies)
        if self.wave_manager.upgrade_ready:
            self.show_upgrade_screen()
            return

        for bullet in self.bullets:
            bullet.update(dt)

        for zombie in self.zombies:
            zombie.update(dt, self.player.pos)

        for particle in self.particles:
            particle.update(dt)

        for powerup in self.powerups:
            powerup.update(dt)

        self.handle_collisions()
        self.handle_powerup_pickups()

        self.bullets = [bullet for bullet in self.bullets if bullet.alive]
        self.zombies = [zombie for zombie in self.zombies if zombie.alive]
        self.particles = [particle for particle in self.particles if particle.is_alive()]
        self.powerups = [powerup for powerup in self.powerups if powerup.alive]

        if self.player.health <= 0:
            self.save_high_score()
            self.state = self.GAME_OVER

    def update_reloading(self, dt):
        if not self.reloading:
            return

        self.reload_timer += dt * 1000
        if self.reload_timer >= self.get_current_reload_time():
            self.weapon_ammo[self.current_weapon_key] = self.get_current_magazine_size()
            self.reloading = False
            self.reload_timer = 0

    def show_upgrade_screen(self):
        self.state = self.UPGRADE
        self.reloading = False
        self.reload_timer = 0
        self.bullets.clear()
        self.upgrade_choices = random.sample(self.get_all_upgrades(), 3)

    def get_all_upgrades(self):
        return [
            {
                "name": "Damage Up",
                "description": "Bullets deal +10 damage.",
                "kind": "damage",
            },
            {
                "name": "Bigger Magazine",
                "description": "Magazine size increases by 3.",
                "kind": "magazine",
            },
            {
                "name": "Faster Reload",
                "description": "Reload time is slightly shorter.",
                "kind": "reload",
            },
            {
                "name": "Max Health Up",
                "description": "Gain +20 max health and heal 25 HP.",
                "kind": "health",
            },
            {
                "name": "Move Speed Up",
                "description": "Move speed increases slightly.",
                "kind": "speed",
            },
        ]

    def choose_upgrade(self, mouse_pos):
        selected_upgrade = self.ui.get_clicked_upgrade(self.upgrade_choices, mouse_pos)
        if selected_upgrade is None:
            return

        self.apply_upgrade(selected_upgrade)
        self.upgrade_choices = []
        self.state = self.PLAYING
        self.start_next_wave()

    def apply_upgrade(self, upgrade):
        if upgrade["kind"] == "damage":
            self.damage_bonus += 10
        elif upgrade["kind"] == "magazine":
            self.magazine_bonus += 3
            for weapon_key in self.weapons:
                self.weapon_ammo[weapon_key] += 3
        elif upgrade["kind"] == "reload":
            self.reload_bonus += 150
        elif upgrade["kind"] == "health":
            self.player.max_health += 20
            self.player.health = min(self.player.max_health, self.player.health + 25)
        elif upgrade["kind"] == "speed":
            self.player.speed += 25

    def update_boosts(self, dt):
        expired_boosts = []
        for boost_type in self.active_boosts:
            self.active_boosts[boost_type] -= dt
            if self.active_boosts[boost_type] <= 0:
                expired_boosts.append(boost_type)

        for boost_type in expired_boosts:
            if boost_type == "speed":
                self.player.speed -= 70
            del self.active_boosts[boost_type]

    def try_drop_powerup(self, pos):
        drop_chance = POWERUP_DROP_CHANCE * self.get_difficulty_config()["drop_chance"]
        if random.random() > drop_chance:
            return

        powerup_type = random.choice(("health", "ammo", "rapid", "damage", "speed"))
        self.powerups.append(PowerUp(pos, powerup_type))

    def handle_powerup_pickups(self):
        for powerup in self.powerups:
            if powerup.alive and powerup.collides_with_player(self.player):
                self.apply_powerup(powerup.powerup_type)
                self.create_pickup_particles(powerup.pos, PowerUp.TYPES[powerup.powerup_type]["color"])
                self.sound_manager.play("powerup")
                powerup.alive = False

    def apply_powerup(self, powerup_type):
        if powerup_type == "health":
            self.player.health = min(self.player.max_health, self.player.health + 25)
        elif powerup_type == "ammo":
            self.weapon_ammo[self.current_weapon_key] = self.get_current_magazine_size()
            self.reloading = False
            self.reload_timer = 0
        elif powerup_type == "rapid":
            self.active_boosts["rapid"] = BOOST_DURATION
        elif powerup_type == "damage":
            self.active_boosts["damage"] = BOOST_DURATION
        elif powerup_type == "speed":
            if "speed" not in self.active_boosts:
                self.player.speed += 70
            self.active_boosts["speed"] = BOOST_DURATION

    def handle_collisions(self):
        for zombie in self.zombies:
            if zombie.pos.distance_to(self.player.pos) <= zombie.radius + self.player.radius:
                if self.player.take_damage(zombie.damage):
                    self.shake_timer = SCREEN_SHAKE_TIME
                    self.sound_manager.play("player_damage")

            for bullet in self.bullets:
                if bullet.alive and zombie.alive and bullet.pos.distance_to(zombie.pos) <= bullet.radius + zombie.radius:
                    zombie.take_damage(bullet.damage)
                    bullet.alive = False
                    self.create_hit_particles(bullet.pos)
                    self.sound_manager.play("zombie_hit")

                    if not zombie.alive:
                        self.score += zombie.score_value
                        self.zombies_killed += 1
                        self.sound_manager.play("zombie_death")
                        self.try_drop_powerup(zombie.pos)

    def create_hit_particles(self, pos):
        for _ in range(HIT_PARTICLE_COUNT):
            self.particles.append(HitParticle(pos))

    def create_pickup_particles(self, pos, color):
        for _ in range(12):
            self.particles.append(HitParticle(pos, color))

    def get_boss_zombie(self):
        for zombie in self.zombies:
            if zombie.zombie_type == "boss" and zombie.alive:
                return zombie
        return None

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.state == self.MENU:
            self.ui.draw_menu(self.screen, self.high_score, self.settings_data["difficulty"])
        elif self.state == self.SETTINGS:
            self.ui.draw_settings_menu(self.screen, self.settings_data)
        elif self.state == self.CONTROLS:
            self.ui.draw_controls_screen(self.screen, self.previous_state == self.PAUSED)
        else:
            world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.ui.draw_background(world_surface)

            for bullet in self.bullets:
                bullet.draw(world_surface)
            for zombie in self.zombies:
                zombie.draw(world_surface)
            for powerup in self.powerups:
                powerup.draw(world_surface, self.powerup_font)
            for particle in self.particles:
                particle.draw(world_surface)

            self.player.draw(world_surface)
            self.screen.blit(world_surface, self.get_screen_shake_offset())
            self.ui.draw_hud(
                self.screen,
                self.player,
                self.score,
                self.wave_manager.wave,
                len(self.zombies),
                max(0, self.wave_manager.zombies_to_spawn - self.wave_manager.spawned_this_wave),
                self.get_current_ammo(),
                self.get_current_magazine_size(),
                self.reloading,
                self.get_current_weapon_name(),
                self.active_boosts,
            )
            if self.settings_data["show_controls"]:
                self.ui.draw_controls_help(self.screen, self.settings_data["difficulty"])
            self.ui.draw_vignette(self.screen)

            boss = self.get_boss_zombie()
            if boss is not None:
                self.ui.draw_boss_health_bar(self.screen, boss)

            if self.boss_wave_text_timer > 0:
                self.ui.draw_boss_wave_text(self.screen, self.boss_wave_text_timer)

            if DEBUG_MODE:
                self.draw_debug_text()

            if self.state == self.PAUSED:
                self.ui.draw_pause_menu(self.screen)

            if self.state == self.UPGRADE:
                self.ui.draw_upgrade_screen(self.screen, self.upgrade_choices)

            if self.state == self.GAME_OVER:
                self.ui.draw_game_over(
                    self.screen,
                    self.score,
                    self.wave_manager.wave,
                    self.high_score,
                    self.zombies_killed,
                )

        pygame.display.flip()

    def get_screen_shake_offset(self):
        if self.shake_timer <= 0:
            return (0, 0)

        strength = int(SCREEN_SHAKE_STRENGTH * (self.shake_timer / SCREEN_SHAKE_TIME))
        return (random.randint(-strength, strength), random.randint(-strength, strength))

    def draw_debug_text(self):
        debug_text = self.debug_font.render(f"DEBUG zombie count: {len(self.zombies)}", True, (255, 255, 255))
        self.screen.blit(debug_text, (34, SCREEN_HEIGHT - 34))
