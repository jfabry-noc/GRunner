#!/usr/bin/env python3
import pygame
import sys

from random import randint, choice



PLAYER_INTERVAL = 15
BACKGROUND_INTERVAL = 5
SCALE_INTERVAL = 0.003
FRAME_RATE = 30

# Class for tracking impediments, good or bad.
class Impediment(pygame.sprite.Sprite):
    def __init__(self, category: str):
        """
        Objects the player can interact with.

        Args:
            category (str): Object type. One of "apple", "dell", "vim", or "vscode".
        """
        super().__init__()
        if category.lower() == "vim":
            self.image = pygame.image.load("static/vim.png")
        elif category.lower() == "apple":
            self.image = pygame.image.load("static/apple.png")
        elif category.lower() == "dell":
            self.image = pygame.image.load("static/dell.png")
        elif category.lower() == "vscode":
            self.image = pygame.image.load("static/vscode.png")

        self.rect = self.image.get_rect(center = (randint(900, 1100), randint(30, 370)))

    def update(self, interval: int, scale: float):
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

    def destroy(self):
        """
        Manages the cleanup of impediments which are off the screen.
        """
        if self.rect.x <= -100:
            self.kill()

# Class for Garrett Prime.
class GPrime(pygame.sprite.Sprite):
    def __init__(self, interval: int):
        """
        Sprite child class to represent Garrett Prime, the player.

        Attributes:
            interval (int): Movement interval that corresponds to key presses.
        """
        super().__init__()
        self.interval = interval
        self.image = pygame.transform.rotozoom(pygame.image.load("static/g_base.gif").convert_alpha(), 0, 2.5)
        self.rect = self.image.get_rect(center = (80, 200))

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= self.interval
            if self.rect.top <= 0:
                self.rect.top = 0
        elif keys[pygame.K_DOWN]:
            self.rect.y += self.interval
            if self.rect.bottom >= 400:
                self.rect.bottom = 400

    def update(self):
        self.player_input()

class GRunner:
    def __init__(self) -> None:
        """
        Initializes the game object.
        """
        pygame.init()
        pygame.display.set_caption("G Runner")
        self.tick_rate = FRAME_RATE
        self.score = 0
        self.screen = pygame.display.set_mode((800, 400))
        self.clock = pygame.time.Clock()
        self.background_surf = pygame.image.load("static/city.png").convert()
        self.background_rect = self.background_surf.get_rect(topleft = (0, 0))
        self.font = pygame.font.Font("fonts/Prompt-Medium.ttf", 40)

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
        pygame.time.set_timer(self.impediment_timer, 1200)

    def print_background(self):
        """
        Adjusts the background image.
        """
        self.background_rect = self.background_surf.get_rect(topleft = (self.background_rect.x - (self.movement_interval + (self.movement_interval * self.movement_scale)), 0))
        if self.background_rect.right <= 800:
            self.background_rect.left = 0
        self.screen.blit(self.background_surf, self.background_rect)

    def display_score(self, increase: int = 0):
        """
        Displays the score. If a number is passed, the score will be incremented
        by that amount.

        Args:
            increase (int): Amount by which to increment the score.
        """
        self.score += increase
        self.score_surf = self.font.render(f"Score: {self.score}", False, "#8F3A84")
        self.score_rect = self.score_surf.get_rect(center = (400, 40))
        self.screen.blit(self.score_surf, self.score_rect)

    def run(self) -> None:
        """
        Starts game execution.
        """
        while True:
            self.movement_scale += SCALE_INTERVAL
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == self.impediment_timer:
                    self.impediment.add(Impediment(choice(["vim", "apple", "vscode", "dell"])))

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            # Render the background first.
            self.print_background()
            self.display_score()

            # Draw the player.
            self.gprime.draw(self.screen)
            self.gprime.update()

            # Draw the impediment(s).
            self.impediment.draw(self.screen)
            self.impediment.update(self.movement_interval, self.movement_scale)

            self.clock.tick(self.tick_rate)

if __name__ == "__main__":
    game = GRunner()
    game.run()

