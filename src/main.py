#!/usr/bin/env python3
import pygame
import sys

from random import randint, choice


# Various settings used through the game.
PLAYER_INTERVAL = 15
BACKGROUND_INTERVAL = 5
SCALE_INTERVAL = 0.003
IMPEDIMENT_INTERVAL = 1000
FRAME_RATE = 30
POINT_INCREMENT = 5
SPAWN_INTERVAL = 12
MUSIC_VOLUME = 0.2
COLLECT_VOLUME = 1.0
FAIL_VOLUME = 0.4
EFFECT_CHANNEL = 1

# Class for tracking impediments, good or bad.
class Impediment(pygame.sprite.Sprite):
    def __init__(self, category: str) -> None:
        """
        Objects the player can interact with.

        Args:
            category (str): Object type. One of "apple", "dell", "vim", or "vscode".
        """
        super().__init__()
        self.category = category.lower()
        if self.category == "vim":
            self.image = pygame.image.load("static/images/vim.png")
        elif self.category == "apple":
            self.image = pygame.image.load("static/images/apple.png")
        elif self.category == "dell":
            self.image = pygame.image.load("static/images/dell.png")
        elif self.category == "vscode":
            self.image = pygame.image.load("static/images/vscode.png")

        self.rect = self.image.get_rect(center = (randint(900, 1100), randint(30, 370)))

    def update(self, interval: int, scale: float) -> None:
        """
        Upates the position of the impediment. Takes an integer for how much
        the X axis should change and a float for the exponential scaling to
        increase the speed over time.

        Args:
            interval (int): Baseline for how much the axis should change.
            scale (float): Scale for increasing the rate of change.
        """
        self.rect.x = self.rect.x - (interval + (interval * scale))
        self.destroy()

    def destroy(self) -> None:
        """
        Manages the cleanup of impediments which are off the screen.
        """
        if self.rect.x <= -100:
            self.kill()

# Class for Garrett Prime.
class GPrime(pygame.sprite.Sprite):
    def __init__(self, interval: int) -> None:
        """
        Sprite child class to represent Garrett Prime, the player.

        Attributes:
            interval (int): Movement interval that corresponds to key presses.
        """
        super().__init__()
        self.interval = interval
        self.garrett_teeth = pygame.transform.rotozoom(pygame.image.load("static/images/gprime_0.png").convert_alpha(), 0, 0.4)
        self.garrett_mouth = pygame.transform.rotozoom(pygame.image.load("static/images/gprime_1.png").convert_alpha(), 0, 0.4)
        self.garrett_fly = [self.garrett_teeth, self.garrett_mouth]
        self.animation_index = 0
        self.image = self.garrett_fly[self.animation_index]
        self.rect = self.image.get_rect(center = (80, 200))

    def player_input(self) -> None:
        """
        Gathers player input and moves Garrett. Up and Down are the only
        valid inputs.
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= self.interval
            if self.rect.top <= 0:
                self.rect.top = 0
        elif keys[pygame.K_DOWN]:
            self.rect.y += self.interval
            if self.rect.bottom >= 400:
                self.rect.bottom = 400

    def reset(self) -> None:
        """
        Resets Garrett on the y-axis. Used to revert position when the game
        ends.
        """
        self.rect.center = (80, 200)

    def update_animation(self) -> None:
        """
        Updates the animation between the two frames.
        """
        self.animation_index += 0.1
        if self.animation_index >= len(self.garrett_fly):
            self.animation_index = 0
        self.image = self.garrett_fly[int(self.animation_index)]

    def update(self) -> None:
        """
        Meta class to process everything involving updating Garrett.
        """
        self.player_input()
        self.update_animation()

class GRunner:
    def __init__(self) -> None:
        """
        Initializes the game object.
        """
        pygame.init()
        pygame.display.set_caption("GRunner")
        self.tick_rate = FRAME_RATE
        self.score = 0
        self.high_score = 0
        self.round_start = 0
        self.impediment_increase = SPAWN_INTERVAL
        self.impediment_interval = IMPEDIMENT_INTERVAL
        self.screen = pygame.display.set_mode((800, 400))
        self.clock = pygame.time.Clock()
        self.background_surf = pygame.image.load("static/images/city.png").convert()
        self.background_rect = self.background_surf.get_rect(topleft = (0, 0))
        self.score_font = pygame.font.Font("static/fonts/Prompt-Medium.ttf", 40)
        self.title_font = pygame.font.Font("static/fonts/Prompt-Medium.ttf", 75)
        self.text_font = pygame.font.Font("static/fonts/Prompt-Medium.ttf", 35)
        self.state = "title"
        self.player_intro_surf = pygame.image.load("static/images/gprime_0.png").convert_alpha()
        self.player_intro_surf = pygame.transform.rotozoom(self.player_intro_surf, 0, 0.5)
        self.player_intro_rect = self.player_intro_surf.get_rect(center = (400, 175))

        pygame.mixer.init()
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        self.title_music = pygame.mixer.Sound("static/audio/ObservingTheStar.ogg")
        self.game_music = pygame.mixer.Sound("static/audio/Drifting_Beyond_the_Stars.ogg")
        self.collection_sound = pygame.mixer.Sound("static/audio/coin.wav")
        self.failure_sound = pygame.mixer.Sound("static/audio/qubodup-PowerDrain.ogg")
        self.title_music.set_volume(MUSIC_VOLUME)
        self.game_music.set_volume(MUSIC_VOLUME)
        self.collection_sound.set_volume(COLLECT_VOLUME)
        self.failure_sound.set_volume(FAIL_VOLUME)

        # Define properties for how rapidly objects move.
        self.movement_interval = BACKGROUND_INTERVAL
        self.movement_scale = 0.0

        # Create Garrett Prime.
        self.gprime = pygame.sprite.GroupSingle()
        self.gprime.add(GPrime(PLAYER_INTERVAL))

        # Create the group to hold the obstacles.
        self.impediment = pygame.sprite.Group()

        # Create a timer for spawning obstacles.
        self.impediment_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.impediment_timer, self.impediment_interval)

    def print_background(self) -> None:
        """
        Adjusts the background image.
        """
        self.background_rect = self.background_surf.get_rect(topleft = (self.background_rect.x - (self.movement_interval + (self.movement_interval * self.movement_scale)), 0))
        if self.background_rect.right <= 800:
            self.background_rect.left = 0
        self.screen.blit(self.background_surf, self.background_rect)

    def display_score(self, increase: int = 0) -> None:
        """
        Displays the score. If a number is passed, the score will be incremented
        by that amount.

        Args:
            increase (int): Amount by which to increment the score.
        """
        self.score += increase
        self.score_surf = self.score_font.render(f"Score: {self.score}", False, "#8F3A84")
        self.score_rect = self.score_surf.get_rect(center = (400, 40))
        self.screen.blit(self.score_surf, self.score_rect)

    def detect_collision(self) -> None:
        """
        Checks if the player has collided with an impediment.
        """
        # Returns an empty list if there is no collision.
        sprite_collision = pygame.sprite.spritecollide(self.gprime.sprite, self.impediment, False)
        for single_sprite in sprite_collision:
            if single_sprite.category == "vim" or single_sprite.category == "apple":
                pygame.mixer.Channel(EFFECT_CHANNEL).play(self.collection_sound)
                self.score += POINT_INCREMENT
                single_sprite.kill()
            elif single_sprite.category == "dell" or single_sprite.category == "vscode":
                pygame.mixer.Channel(EFFECT_CHANNEL).play(self.failure_sound)
                self.state = "over"
                self.impediment.empty()
                self.gprime.sprite.reset()

    def run(self) -> None:
        """
        Starts game execution.
        """
        while True:
        # Process events.
            for event in pygame.event.get():
                if self.state == "running":
                    if event.type == self.impediment_timer:
                        self.impediment.add(Impediment(choice(["vim", "apple", "vscode", "dell"])))
                elif self.state == "title" or self.state == "over":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = "running"
                        self.round_start = int(pygame.time.get_ticks() / 1000)

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit(0)

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            # Display the title screen.
            if self.state == "title":
                self.title_music.play(loops=-1)
                self.screen.fill((51, 204, 205))
                self.screen.blit(self.player_intro_surf, self.player_intro_rect)

                title_surface = self.title_font.render("GRunner", False, "#8F3A84")
                title_rect = title_surface.get_rect(center = (400, 50))
                self.screen.blit(title_surface, title_rect)

                text_surface = self.text_font.render("Help Garrett Prime!", False, "#8F3A84")
                text_rect = text_surface.get_rect(center = (400, 275))
                self.screen.blit(text_surface, text_rect)

                instruct_surface = self.text_font.render("Hit Enter To Play", False, "#8F3A84")
                instruct_rect = instruct_surface.get_rect(center = (400, 350))
                self.screen.blit(instruct_surface, instruct_rect)

            elif self.state == "over":
                self.game_music.stop()
                self.title_music.play(loops=-1)
                if self.score > self.high_score:
                    self.high_score = self.score
                self.score = 0
                self.movement_scale = 0
                self.impediment_interval = IMPEDIMENT_INTERVAL
                self.impediment_increase = SPAWN_INTERVAL
                pygame.time.set_timer(self.impediment_timer, self.impediment_interval)

                self.screen.fill((51, 204, 205))
                self.screen.blit(self.player_intro_surf, self.player_intro_rect)

                title_surface = self.title_font.render("Game Over!", False, "#8F3A84")
                title_rect = title_surface.get_rect(center = (400, 50))
                self.screen.blit(title_surface, title_rect)

                text_surface = self.text_font.render(f"High Score: {self.high_score}", False, "#8F3A84")
                text_rect = text_surface.get_rect(center = (400, 275))
                self.screen.blit(text_surface, text_rect)

                instruct_surface = self.text_font.render("Hit Enter To Play Again", False, "#8F3A84")
                instruct_rect = instruct_surface.get_rect(center = (400, 350))
                self.screen.blit(instruct_surface, instruct_rect)

            elif self.state == "running":
                self.title_music.stop()
                self.game_music.play(loops=-1)
                self.movement_scale += SCALE_INTERVAL

                # Check if the spawn rates needs to be increased.
                if int(pygame.time.get_ticks() / 1000) - self.round_start > self.impediment_increase:
                    self.impediment_increase += SPAWN_INTERVAL
                    self.impediment_interval = round(0.75 * self.impediment_interval)
                    pygame.time.set_timer(self.impediment_timer, self.impediment_interval)

                # Render the background first.
                self.print_background()

                # Draw the impediment(s).
                self.impediment.draw(self.screen)
                self.impediment.update(self.movement_interval, self.movement_scale)

                # Draw the score so it's always on top of the impediments.
                self.display_score()

                # Draw the player.
                self.gprime.draw(self.screen)
                self.gprime.update()

                # Check for a collision.
                self.detect_collision()

            pygame.display.update()
            self.clock.tick(self.tick_rate)

if __name__ == "__main__":
    game = GRunner()
    game.run()

