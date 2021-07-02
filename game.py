import random
from collections import namedtuple
from enum import Enum

import numpy as np
import pygame

pygame.init()
font = pygame.font.Font('arial.ttf', 25)


class Direction(Enum):
    IDLE = 0
    N = 1
    NE = 2
    E = 3
    SE = 4
    S = 5
    SW = 6
    W = 7
    NW = 8


Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 20


class Game:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Kiting')
        self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        # init game state
        self.position = Point(self.w / 2, self.h / 2)
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food == self.position:
            self._place_food()

    def get_human_action(self):
        action = [1, 0, 0, 0, 0]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            action = [0, 1, 0, 0, 0]
        elif keys[pygame.K_RIGHT]:
            action = [0, 0, 1, 0, 0]
        elif keys[pygame.K_DOWN]:
            action = [0, 0, 0, 1, 0]
        elif keys[pygame.K_LEFT]:
            action = [0, 0, 0, 0, 1]
        return action

    def play_step(self, action):
        # 1. collect user input

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                quit()

        # 2. move
        self._move(action)  # update the head

        reward = 0
        # 3. check if game over
        game_over = False
        if self.is_collision(self.position):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.position == self.food:
            self.score += 1
            reward = 10
            self._place_food()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score

    def is_collision(self, pt):
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        return False

    def _update_ui(self):
        self.display.fill(BLACK)
        pt = self.position
        pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        pygame.draw.rect(self.display, RED, pygame.Rect(
            self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        text = font.render('Score: ' + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):
        if np.array_equal(action, [1, 0, 0, 0, 0]):
            direction = Direction.IDLE
        elif np.array_equal(action, [0, 1, 0, 0, 0]):
            direction = Direction.N
        elif np.array_equal(action, [0, 0, 1, 0, 0]):
            direction = Direction.E
        elif np.array_equal(action, [0, 0, 0, 1, 0]):
            direction = Direction.S
        else:
            direction = Direction.W

        x = self.position.x
        y = self.position.y
        if direction == Direction.E:
            x += BLOCK_SIZE
        elif direction == Direction.W:
            x -= BLOCK_SIZE
        elif direction == Direction.S:
            y += BLOCK_SIZE
        elif direction == Direction.N:
            y -= BLOCK_SIZE

        self.position = Point(x, y)


if __name__ == '__main__':
    game = Game()

    # game loop
    while True:
        action = game.get_human_action()
        _, game_over, score = game.play_step(action)

        if game_over == True:
            break

    print('Final Score', score)

    pygame.quit()
