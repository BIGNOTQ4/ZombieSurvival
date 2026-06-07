import pygame

from settings import (
    ACCENT,
    ACCENT_DARK,
    BLACK,
    BLOOD,
    FLOOR_COLOR,
    GRAY,
    GRID_COLOR,
    GRID_DARK,
    GREEN,
    GREEN_DARK,
    PANEL_COLOR,
    PANEL_LIGHT,
    PLAYER_MAX_HEALTH,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
    VERSION,
    WHITE,
    YELLOW,
)


class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

    def draw(self, surface):
        mouse_over = self.rect.collidepoint(pygame.mouse.get_pos())
        color = ACCENT if mouse_over else ACCENT_DARK
        shadow_rect = self.rect.move(0, 7)

        pygame.draw.rect(surface, (5, 8, 13), shadow_rect, border_radius=16)
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        pygame.draw.rect(surface, (148, 199, 255), self.rect.inflate(-4, -4), width=2, border_radius=12)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class UI:
    def __init__(self):
        self.title_font = pygame.font.Font(None, 104)
        self.large_font = pygame.font.Font(None, 58)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 22)

        self.start_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 + 46, 220, 54), "Start", self.medium_font)
        self.settings_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 + 112, 220, 54), "Settings", self.medium_font)
        self.controls_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 + 178, 220, 54), "Controls", self.medium_font)
        self.back_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT - 112, 220, 54), "Back", self.medium_font)
        self.resume_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 - 16, 220, 50), "Resume", self.medium_font)
        self.pause_controls_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 + 46, 220, 50), "Controls", self.medium_font)
        self.main_menu_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 + 108, 220, 50), "Main Menu", self.medium_font)
        self.restart_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 + 100, 220, 50), "Restart", self.medium_font)
        self.game_over_menu_button = Button((SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 + 160, 220, 50), "Main Menu", self.medium_font)
        self.volume_down_button = Button((SCREEN_WIDTH / 2 + 50, 238, 52, 42), "-", self.medium_font)
        self.volume_up_button = Button((SCREEN_WIDTH / 2 + 170, 238, 52, 42), "+", self.medium_font)
        self.sfx_button = Button((SCREEN_WIDTH / 2 + 50, 300, 172, 42), "Toggle", self.small_font)
        self.help_button = Button((SCREEN_WIDTH / 2 + 50, 362, 172, 42), "Toggle", self.small_font)
        self.difficulty_buttons = {
            "Easy": Button((SCREEN_WIDTH / 2 - 230, 462, 140, 46), "Easy", self.small_font),
            "Normal": Button((SCREEN_WIDTH / 2 - 70, 462, 140, 46), "Normal", self.small_font),
            "Hard": Button((SCREEN_WIDTH / 2 + 90, 462, 140, 46), "Hard", self.small_font),
        }

    def draw_menu(self, surface, high_score, difficulty):
        self.draw_background(surface)
        self.draw_vignette(surface)

        glow = pygame.Surface((620, 190), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (88, 166, 255, 24), glow.get_rect())
        surface.blit(glow, (SCREEN_WIDTH / 2 - 310, SCREEN_HEIGHT / 2 - 210))

        title_shadow = self.title_font.render(TITLE, True, BLACK)
        title_shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH / 2 + 4, SCREEN_HEIGHT / 2 - 116))
        surface.blit(title_shadow, title_shadow_rect)
        title = self.title_font.render(TITLE, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 120))
        surface.blit(title, title_rect)

        subtitle = self.small_font.render("Survive the waves. Keep moving. Watch your ammo.", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 48))
        surface.blit(subtitle, subtitle_rect)

        controls = self.tiny_font.render(
            "WASD move  |  Mouse aim  |  Click shoot  |  R reload  |  1/2/3 weapons  |  ESC pause",
            True,
            (105, 117, 136),
        )
        controls_rect = controls.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 14))
        surface.blit(controls, controls_rect)

        high_score_text = self.small_font.render(f"High Score: {high_score}", True, YELLOW)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 28))
        surface.blit(high_score_text, high_score_rect)

        difficulty_text = self.tiny_font.render(f"Difficulty: {difficulty}", True, ACCENT)
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 250))
        surface.blit(difficulty_text, difficulty_rect)

        version_text = self.tiny_font.render(f"v{VERSION}", True, (105, 117, 136))
        surface.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - 24, SCREEN_HEIGHT - 34))

        self.start_button.draw(surface)
        self.settings_button.draw(surface)
        self.controls_button.draw(surface)

    def draw_hud(
        self,
        surface,
        player,
        score,
        wave,
        zombies_alive,
        zombies_remaining,
        ammo,
        magazine_size,
        reloading,
        weapon_name,
        active_boosts,
    ):
        self.draw_top_panel(surface)
        self.draw_health_bar(surface, player.health, player.max_health)

        self.draw_stat(surface, "Ammo", f"{ammo}/{magazine_size}", 430, 28, YELLOW if not reloading else GRAY)
        self.draw_stat(surface, "Weapon", weapon_name, 570, 28, ACCENT)
        self.draw_stat(surface, "Score", str(score), 760, 28, WHITE)
        self.draw_stat(surface, "Wave", str(wave), SCREEN_WIDTH - 310, 28, ACCENT)
        self.draw_stat(surface, "Zombies", str(zombies_alive + zombies_remaining), SCREEN_WIDTH - 160, 28, BLOOD)

        if reloading:
            reload_text = self.medium_font.render("Reloading...", True, YELLOW)
            reload_rect = reload_text.get_rect(center=(SCREEN_WIDTH / 2, 92))
            surface.blit(reload_text, reload_rect)

        self.draw_active_boosts(surface, active_boosts)

    def draw_pause_menu(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 420, 320)
        panel.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=22)
        pygame.draw.rect(surface, PANEL_LIGHT, panel, width=2, border_radius=22)

        title = self.large_font.render("Paused", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 96))
        surface.blit(title, title_rect)

        hint = self.tiny_font.render("Press ESC to resume", True, GRAY)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 178))
        surface.blit(hint, hint_rect)
        self.resume_button.draw(surface)
        self.pause_controls_button.draw(surface)
        self.main_menu_button.draw(surface)

    def draw_settings_menu(self, surface, settings):
        self.draw_background(surface)
        self.draw_vignette(surface)

        panel = pygame.Rect(0, 0, 620, 500)
        panel.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=24)
        pygame.draw.rect(surface, PANEL_LIGHT, panel, width=2, border_radius=24)

        title = self.large_font.render("Settings", True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, 160)))

        rows = [
            ("Master Volume", f"{int(settings['master_volume'] * 100)}%", 246),
            ("Sound Effects", "On" if settings["sound_effects"] else "Off", 308),
            ("Show Controls Help", "On" if settings["show_controls"] else "Off", 370),
        ]
        for label, value, y in rows:
            label_surface = self.small_font.render(label, True, GRAY)
            value_surface = self.small_font.render(value, True, WHITE)
            surface.blit(label_surface, (SCREEN_WIDTH / 2 - 230, y))
            surface.blit(value_surface, (SCREEN_WIDTH / 2 - 20, y))

        difficulty_label = self.small_font.render("Difficulty", True, GRAY)
        surface.blit(difficulty_label, (SCREEN_WIDTH / 2 - 230, 430))

        self.volume_down_button.draw(surface)
        self.volume_up_button.draw(surface)
        self.sfx_button.draw(surface)
        self.help_button.draw(surface)
        for difficulty, button in self.difficulty_buttons.items():
            button.draw(surface)
            if difficulty == settings["difficulty"]:
                pygame.draw.rect(surface, YELLOW, button.rect.inflate(8, 8), width=3, border_radius=16)
        self.back_button.draw(surface)

    def draw_controls_screen(self, surface, from_pause=False):
        self.draw_background(surface)
        self.draw_vignette(surface)

        panel = pygame.Rect(0, 0, 560, 440)
        panel.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=24)
        pygame.draw.rect(surface, PANEL_LIGHT, panel, width=2, border_radius=24)

        title = self.large_font.render("Controls", True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, 170)))

        controls = [
            "WASD: Move",
            "Mouse: Aim",
            "Left Click: Shoot",
            "R: Reload",
            "1/2/3: Switch Weapon",
            "ESC: Pause",
        ]
        for index, line in enumerate(controls):
            text = self.small_font.render(line, True, GRAY)
            surface.blit(text, (SCREEN_WIDTH / 2 - 170, 240 + index * 38))

        back_hint = "Back to Pause" if from_pause else "Back"
        self.back_button.text = back_hint
        self.back_button.draw(surface)
        self.back_button.text = "Back"

    def draw_upgrade_screen(self, surface, upgrades):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = self.large_font.render("Wave Complete", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150))
        surface.blit(title, title_rect)

        subtitle = self.small_font.render("Choose one upgrade to continue.", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 105))
        surface.blit(subtitle, subtitle_rect)

        for index, upgrade in enumerate(upgrades):
            card_rect = self.get_upgrade_card_rect(index)
            self.draw_upgrade_card(surface, card_rect, upgrade)

    def get_clicked_upgrade(self, upgrades, mouse_pos):
        for index, upgrade in enumerate(upgrades):
            if self.get_upgrade_card_rect(index).collidepoint(mouse_pos):
                return upgrade
        return None

    def get_upgrade_card_rect(self, index):
        card_width = 300
        card_height = 180
        gap = 34
        total_width = card_width * 3 + gap * 2
        left = SCREEN_WIDTH / 2 - total_width / 2
        top = SCREEN_HEIGHT / 2 - 45
        return pygame.Rect(left + index * (card_width + gap), top, card_width, card_height)

    def draw_upgrade_card(self, surface, rect, upgrade):
        mouse_over = rect.collidepoint(pygame.mouse.get_pos())
        fill_color = (39, 48, 64) if mouse_over else PANEL_COLOR
        border_color = ACCENT if mouse_over else PANEL_LIGHT
        shadow_rect = rect.move(0, 8)

        pygame.draw.rect(surface, (5, 8, 13), shadow_rect, border_radius=18)
        pygame.draw.rect(surface, fill_color, rect, border_radius=18)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=18)

        name = self.medium_font.render(upgrade["name"], True, WHITE)
        surface.blit(name, (rect.x + 24, rect.y + 28))

        description_lines = self.wrap_text(upgrade["description"], self.small_font, rect.width - 48)
        for line_number, line in enumerate(description_lines):
            description = self.small_font.render(line, True, GRAY)
            surface.blit(description, (rect.x + 24, rect.y + 82 + line_number * 28))

        hint = self.tiny_font.render("Click to choose", True, ACCENT if mouse_over else (105, 117, 136))
        surface.blit(hint, (rect.x + 24, rect.bottom - 36))

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)
        return lines

    def draw_game_over(self, surface, score, wave, high_score, zombies_killed):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 520, 430)
        panel.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=22)
        pygame.draw.rect(surface, PANEL_LIGHT, panel, width=2, border_radius=22)

        title = self.large_font.render("Game Over", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 145))
        surface.blit(title, title_rect)

        summary = self.medium_font.render(f"Final Score: {score}", True, WHITE)
        summary_rect = summary.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 88))
        surface.blit(summary, summary_rect)

        high_score_text = self.small_font.render(f"High Score: {high_score}", True, YELLOW)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        surface.blit(high_score_text, high_score_rect)

        wave_text = self.small_font.render(f"Wave Reached: {wave}", True, GRAY)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 14))
        surface.blit(wave_text, wave_rect)

        kills_text = self.small_font.render(f"Zombies Killed: {zombies_killed}", True, GRAY)
        kills_rect = kills_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 22))
        surface.blit(kills_text, kills_rect)

        self.restart_button.draw(surface)
        self.game_over_menu_button.draw(surface)

    def draw_background(self, surface):
        surface.fill(FLOOR_COLOR)

        for y in range(0, SCREEN_HEIGHT, 48):
            color = GRID_COLOR if y % 96 == 0 else GRID_DARK
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y), 1)
        for x in range(0, SCREEN_WIDTH, 48):
            color = GRID_COLOR if x % 96 == 0 else GRID_DARK
            pygame.draw.line(surface, color, (x, 0), (x, SCREEN_HEIGHT), 1)

        for x in range(0, SCREEN_WIDTH, 192):
            for y in range(0, SCREEN_HEIGHT, 192):
                pygame.draw.circle(surface, (22, 28, 38), (x + 96, y + 96), 2)

    def draw_top_panel(self, surface):
        panel = pygame.Rect(18, 16, SCREEN_WIDTH - 36, 104)
        shadow = panel.move(0, 6)
        pygame.draw.rect(surface, (5, 8, 13), shadow, border_radius=20)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=18)
        pygame.draw.rect(surface, PANEL_LIGHT, panel, width=2, border_radius=18)

    def draw_health_bar(self, surface, health, max_health):
        label = self.tiny_font.render("Health", True, GRAY)
        surface.blit(label, (34, 24))

        bar_rect = pygame.Rect(34, 52, 340, 26)
        health_ratio = max(0, health / max_health)
        fill_rect = bar_rect.copy()
        fill_rect.width = int(bar_rect.width * health_ratio)

        fill_color = GREEN if health_ratio > 0.35 else RED
        fill_shadow = GREEN_DARK if health_ratio > 0.35 else (150, 45, 45)

        pygame.draw.rect(surface, fill_shadow, bar_rect, border_radius=10)
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=10)
        pygame.draw.rect(surface, PANEL_LIGHT, bar_rect, width=2, border_radius=10)

        value = self.small_font.render(f"{health}/{max_health}", True, WHITE)
        value_rect = value.get_rect(center=bar_rect.center)
        surface.blit(value, value_rect)

    def draw_stat(self, surface, label, value, x, y, color):
        label_surface = self.tiny_font.render(label, True, GRAY)
        value_surface = self.medium_font.render(value, True, color)
        surface.blit(label_surface, (x, y))
        surface.blit(value_surface, (x, y + 22))

    def draw_active_boosts(self, surface, active_boosts):
        if not active_boosts:
            return

        names = {
            "rapid": "Rapid Fire",
            "damage": "Damage Boost",
            "speed": "Speed Boost",
        }
        x = 430
        y = 86

        for boost_type, time_left in active_boosts.items():
            text = self.tiny_font.render(f"{names[boost_type]} {time_left:.1f}s", True, ACCENT)
            surface.blit(text, (x, y))
            x += text.get_width() + 22

    def draw_controls_help(self, surface, difficulty):
        help_text = "WASD move | Mouse aim | Click shoot | R reload | 1/2/3 weapons | ESC pause"
        text = self.tiny_font.render(help_text, True, (105, 117, 136))
        difficulty_text = self.tiny_font.render(f"Difficulty: {difficulty}", True, ACCENT)
        surface.blit(text, (34, SCREEN_HEIGHT - 56))
        surface.blit(difficulty_text, (34, SCREEN_HEIGHT - 32))

    def draw_boss_health_bar(self, surface, boss):
        bar_rect = pygame.Rect(0, 0, 620, 26)
        bar_rect.center = (SCREEN_WIDTH / 2, 150)
        health_ratio = max(0, boss.health / boss.max_health)
        fill_rect = bar_rect.copy()
        fill_rect.width = int(bar_rect.width * health_ratio)

        label = self.medium_font.render("BOSS", True, RED)
        label_rect = label.get_rect(center=(SCREEN_WIDTH / 2, 124))

        pygame.draw.rect(surface, (5, 8, 13), bar_rect.move(0, 5), border_radius=12)
        pygame.draw.rect(surface, (65, 20, 35), bar_rect, border_radius=12)
        pygame.draw.rect(surface, RED, fill_rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, bar_rect, width=2, border_radius=12)
        surface.blit(label, label_rect)

    def draw_boss_wave_text(self, surface, timer):
        alpha = min(255, int(255 * min(1, timer / 0.6)))
        text_surface = self.large_font.render("BOSS WAVE", True, RED)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 170))
        surface.blit(text_surface, text_rect)

    def draw_vignette(self, surface):
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        edge_color = (0, 0, 0, 18)
        for thickness, alpha in ((0, 110), (24, 80), (52, 48), (88, 26)):
            rect = pygame.Rect(thickness, thickness, SCREEN_WIDTH - thickness * 2, SCREEN_HEIGHT - thickness * 2)
            pygame.draw.rect(vignette, (0, 0, 0, alpha), rect, width=26, border_radius=28)
        pygame.draw.rect(vignette, edge_color, vignette.get_rect(), width=18)
        surface.blit(vignette, (0, 0))
