import random
from collections import namedtuple
from enum import Enum

import numpy as np
import pygame

from distance import get_chessboard_distance

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


class Game:

    def __init__(self, w=640, h=480, speed=120, lethal_distance=1, optimal_distance=5):
        self.w = w
        self.h = h
        self.speed = speed
        self.lethal_distance = lethal_distance
        self.optimal_distance = optimal_distance

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('kite-ai')
        self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        # init game state
        self.position = Point(self.w / 2, self.h / 2)
        self.score = 0
        self.enemy = None
        self._place_enemy()
        self.frame_iteration = 0

    def _place_enemy(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.enemy = Point(x, y)
        distance = get_chessboard_distance(self.position, self.enemy) / BLOCK_SIZE
        if distance <= self.lethal_distance:
            self._place_enemy()

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
        reward = 0
        self.frame_iteration += 1

        # inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                quit()

        # move based on action
        self._move(action)

        # increase score if distance is less than or equal to optimal distance
        # else, give reward based on how close the player is to enemy
        distance = get_chessboard_distance(self.position, self.enemy) / BLOCK_SIZE
        if distance <= self.optimal_distance:
            reward = 1

        # check if game over
        game_over = (
            self.is_collision(self.position) or  # collies with wall
            (self.frame_iteration > 100 and self.score == 0) or  # 0 score for too long
            distance <= self.lethal_distance  # colldies with enemy
        )
        game_too_long = self.frame_iteration > 500  # game too long
        if game_over:
            reward = -10
        if game_over or game_too_long:
            return reward, game_over, self.score

        # else:
        #     reward = 1 / distance
        self.score += reward

        # update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)
        # return reward, game over and score
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
            self.enemy.x, self.enemy.y, BLOCK_SIZE, BLOCK_SIZE))
        text = font.render(f'Score: {self.score:.0f}', True, WHITE)
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

    def get_state(self):
        position = self.position
        point_u = Point(position.x, position.y - 20)
        point_r = Point(position.x + 20, position.y)
        point_d = Point(position.x, position.y + 20)
        point_l = Point(position.x - 20, position.y)

        distance_u = (self.position.y - self.enemy.y) / BLOCK_SIZE
        distance_r = (self.enemy.x - self.position.x) / BLOCK_SIZE
        distance_d = (self.enemy.y - self.position.y) / BLOCK_SIZE
        distance_l = (self.position.x - self.enemy.x) / BLOCK_SIZE

        # enemy_u = distance_u > 1
        # enemy_r = distance_r > 1
        # enemy_d = distance_d > 1
        # enemy_l = distance_l > 1

        optimal_u = distance_u == self.optimal_distance
        optimal_r = distance_r == self.optimal_distance
        optimal_d = distance_d == self.optimal_distance
        optimal_l = distance_l == self.optimal_distance

        optimal_low_u = distance_u < self.optimal_distance
        optimal_low_r = distance_r < self.optimal_distance
        optimal_low_d = distance_d < self.optimal_distance
        optimal_low_l = distance_l < self.optimal_distance

        optimal_high_u = distance_u > self.optimal_distance
        optimal_high_r = distance_r > self.optimal_distance
        optimal_high_d = distance_d > self.optimal_distance
        optimal_high_l = distance_l > self.optimal_distance

        state = [
            # wall near
            self.is_collision(point_u),
            self.is_collision(point_r),
            self.is_collision(point_d),
            self.is_collision(point_l),
            # enemy_u,
            # enemy_r,
            # enemy_d,
            # enemy_l,
            optimal_u,
            optimal_r,
            optimal_d,
            optimal_l,
            optimal_low_u,
            optimal_low_r,
            optimal_low_d,
            optimal_low_l,
            optimal_high_u,
            optimal_high_r,
            optimal_high_d,
            optimal_high_l,
        ]
        state = np.array(state, dtype=int)
        return state


if __name__ == '__main__':
    game = Game(speed=30)

    # game loop
    while True:
        action = game.get_human_action()
        _, game_over, score = game.play_step(action)
        print(game.get_state())
        if game_over == True:
            break

    print('Final Score', int(score))

    pygame.quit()
