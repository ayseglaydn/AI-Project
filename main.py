import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1200, 750
window = pygame.display.set_mode((WIDTH, HEIGHT))

FPS = 30
clock = pygame.time.Clock()


class Game():
    def __init__(self, player1, player2, ball_group):
        self.player1 = player1
        self.player2 = player2
        self.ball_group = ball_group

        try:
            self.background = pygame.image.load("background.jpg")
        except:
            self.background = pygame.Surface((WIDTH, HEIGHT))
            self.background.fill((20, 50, 30))

        try:
            self.game_over_screen = pygame.image.load("game_over.jpg")
        except:
            self.game_over_screen = pygame.Surface((WIDTH, HEIGHT))
            self.game_over_screen.fill((50, 20, 20))

        self.player1_score = 0
        self.player2_score = 0
        self.score_value = 5
        self.timer = 60
        self.fps_count = 0

        try:
            self.game_font = pygame.font.Font("game_font.ttf", 40)
        except:
            self.game_font = pygame.font.Font(None, 40)

        try:
            self.wall_sound = pygame.mixer.Sound("score_lost.wav")
            self.hit_sound = pygame.mixer.Sound("hit.wav")
            pygame.mixer.music.load("game_music.wav")
            pygame.mixer.music.play(-1)
        except:
            self.wall_sound = None
            self.hit_sound = None

    def update(self):
        self.fps_count += 1
        if self.fps_count == FPS:
            self.timer -= 1
            self.fps_count = 0
            if self.timer == 0:
                self.finish()

        self.check_collision()
        self.check_score()

    def draw(self):
        window.blit(self.background, (0, 0))

        black = (0, 0, 0)

        score1 = self.game_font.render("Player: " + str(self.player1_score), True, black)
        score1_rect = score1.get_rect()
        score1_rect.topleft = (30, 50)

        score2 = self.game_font.render("AI: " + str(self.player2_score), True, black)
        score2_rect = score2.get_rect()
        score2_rect.topleft = (WIDTH - 200, 50)

        timer_text = self.game_font.render("Time: " + str(self.timer), True, black)
        timer_rect = timer_text.get_rect()
        timer_rect.topleft = (WIDTH // 2 - 80, 50)

        window.blit(score1, score1_rect)
        window.blit(score2, score2_rect)
        window.blit(timer_text, timer_rect)

    def check_collision(self):
        if pygame.sprite.spritecollide(self.player1, self.ball_group, False):
            if self.hit_sound:
                self.hit_sound.play()
            for ball in self.ball_group.sprites():
                ball.dirx *= -1
                if ball.speed <= 15:
                    ball.speed += 0.5

        if pygame.sprite.spritecollide(self.player2, self.ball_group, False):
            if self.hit_sound:
                self.hit_sound.play()
            for ball in self.ball_group.sprites():
                ball.dirx *= -1
                if ball.speed <= 15:
                    ball.speed += 0.5

    def check_score(self):
        for ball in self.ball_group.sprites():
            if ball.rect.left <= 0:
                if self.wall_sound:
                    self.wall_sound.play()
                self.player2_score += self.score_value
                ball.reset()
            if ball.rect.right >= WIDTH:
                if self.wall_sound:
                    self.wall_sound.play()
                self.player1_score += self.score_value
                ball.reset()

    def finish(self):
        global running
        finished = True
        window.blit(self.game_over_screen, (0, 0))

        black = (0, 0, 0)

        if self.player1_score > self.player2_score:
            result_text = "YOU WIN!"
        elif self.player2_score > self.player1_score:
            result_text = "AI WINS!"
        else:
            result_text = "DRAW!"

        result = self.game_font.render(result_text, True, black)
        result_rect = result.get_rect()
        result_rect.center = (WIDTH // 2, HEIGHT // 2)

        retry_text = self.game_font.render("ENTER: Play Again", True, black)
        retry_rect = retry_text.get_rect()
        retry_rect.center = (WIDTH // 2, HEIGHT // 2 + 60)

        window.blit(result, result_rect)
        window.blit(retry_text, retry_rect)
        pygame.display.update()

        while finished:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        finished = False
                if event.type == pygame.QUIT:
                    finished = False
                    running = False

    def reset_game(self):
        self.player1_score = 0
        self.player2_score = 0
        self.timer = 30
        for ball in self.ball_group.sprites():
            ball.reset()


class Player1(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("player1.png")
        except:
            self.image = pygame.Surface((20, 100))
            self.image.fill((0, 100, 255))

        self.rect = self.image.get_rect()
        self.rect.x = 20
        self.rect.centery = HEIGHT // 2
        self.speed = 10

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        elif keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed


class Player2AI(pygame.sprite.Sprite):
    def __init__(self, difficulty="medium"):
        super().__init__()
        try:
            self.image = pygame.image.load("player2.png")
        except:
            self.image = pygame.Surface((20, 100))
            self.image.fill((255, 100, 0))

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 40
        self.rect.centery = HEIGHT // 2

        if difficulty == "easy":
            self.speed = 6
            self.reaction_distance = 400
            self.error_margin = 30
        elif difficulty == "medium":
            self.speed = 8
            self.reaction_distance = 600
            self.error_margin = 15
        else:
            self.speed = 10
            self.reaction_distance = 800
            self.error_margin = 5

    def update(self, ball_group):
        for ball in ball_group.sprites():
            if ball.dirx > 0 and ball.rect.centerx > WIDTH - self.reaction_distance:
                target_y = ball.rect.centery + random.randint(-self.error_margin, self.error_margin)

                if self.rect.centery < target_y - 10 and self.rect.bottom < HEIGHT:
                    self.rect.y += self.speed
                elif self.rect.centery > target_y + 10 and self.rect.top > 0:
                    self.rect.y -= self.speed
            else:
                center = HEIGHT // 2
                if self.rect.centery < center - 5:
                    self.rect.y += self.speed // 2
                elif self.rect.centery > center + 5:
                    self.rect.y -= self.speed // 2


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("ball.png")
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 255, 255))
            pygame.draw.circle(self.image, (255, 255, 0), (10, 10), 10)

        self.rect = self.image.get_rect()
        self.start_x = x
        self.start_y = y
        self.rect.centerx = x
        self.rect.centery = y

        self.dirx = random.choice([-1, 1])
        self.diry = random.choice([-1, 1])
        self.speed = 8

    def update(self):
        self.rect.centerx += self.speed * self.dirx
        self.rect.centery += self.speed * self.diry

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.diry *= -1

    def reset(self):
        self.rect.centerx = WIDTH // 2
        self.rect.centery = random.randint(200, HEIGHT - 200)
        self.dirx = random.choice([-1, 1])
        self.diry = random.choice([-1, 1])
        self.speed = 8


player1_group = pygame.sprite.Group()
player1 = Player1()
player1_group.add(player1)

player2_group = pygame.sprite.Group()
player2 = Player2AI(difficulty="hard")
player2_group.add(player2)

ball_group = pygame.sprite.Group()
ball = Ball(WIDTH // 2, HEIGHT // 2)
ball_group.add(ball)

game = Game(player1, player2, ball_group)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    game.draw()
    game.update()

    player1_group.update()
    player1_group.draw(window)

    player2.update(ball_group)
    player2_group.draw(window)

    ball_group.update()
    ball_group.draw(window)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
