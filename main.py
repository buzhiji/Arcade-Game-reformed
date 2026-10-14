import pygame
import random
import asyncio
import os

async def main():
    pygame.init()

    w = 900
    h = 600

    screen = pygame.display.set_mode((w, h))

    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 28)

    title_image = pygame.image.load(
        os.path.join(os.path.dirname(__file__), "start.png")
    ).convert()
    image_scale = min(w / title_image.get_width(), h / title_image.get_height())
    title_size = (
        int(title_image.get_width() * image_scale),
        int(title_image.get_height() * image_scale),
    )
    title_image = pygame.transform.smoothscale(title_image, title_size)
    title_rect = title_image.get_rect(center=(w // 2, h // 2))
    title_text = font.render("Press SPACE to start", True, (20, 20, 20))
    title_text_rect = title_text.get_rect(center=(w // 2, h - 24))

    title_screen = True
    while title_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                title_screen = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                title_screen = False

        screen.fill((20, 24, 40))
        screen.blit(title_image, title_rect)
        screen.blit(title_text, title_text_rect)
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    story_images = []
    for image_number in range(1, 11):
        image = pygame.image.load(
            os.path.join(os.path.dirname(__file__), f"{image_number}.png")
        ).convert()
        image_scale = min(w / image.get_width(), h / image.get_height())
        image_size = (
            int(image.get_width() * image_scale),
            int(image.get_height() * image_scale),
        )
        image = pygame.transform.smoothscale(image, image_size)
        story_images.append((image, image.get_rect(center=(w // 2, h // 2))))

    for image, image_rect in story_images:
        image_start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - image_start_time < 3000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            screen.fill((20, 24, 40))
            screen.blit(image, image_rect)
            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

    start_time = pygame.time.get_ticks()

    class Enemy:
        detected = False
 
        def __init__(self, x, y):
            self.pos = pygame.math.Vector2(x, y)
            self.speed = 2
            self.rotation = 0
            self.acceleration = 0.05
            self.detected = False
            self.next_shot_time = 2000


        def move(self, ship):
            to_player = ship.pos - self.pos
            distance = to_player.length()

            if distance == 0:
                self.detected = True
                return

            direction_to_player = to_player.normalize()
            forward = pygame.Vector2(0, -1).rotate(self.rotation)
            dot = forward.dot(direction_to_player)

            self.detected = dot >= 0.9 and distance < 400

            if not self.detected:
                self.rotation = (self.rotation + 5) % 360
            if self.detected:
                now = pygame.time.get_ticks()
                self.velocity = direction_to_player * self.speed
                self.pos += self.velocity
                if now >= self.next_shot_time:
                    missiles.append(Missile(self.pos, ship.pos, owner="enemy"))
                    self.next_shot_time = now + 1500

        def draw(self):
            points = [
                pygame.Vector2(0, -22),
                pygame.Vector2(-17, 10),
                pygame.Vector2(17, 10),
            ]
            points = [(int(self.pos.x + p.rotate(self.rotation).x), int(self.pos.y + p.rotate(self.rotation).y)) for p in points]
            pygame.draw.polygon(screen, (255, 0, 0), points, 2)
            nose = pygame.Vector2(0, -28).rotate(self.rotation)
            nose_start = self.pos + pygame.Vector2(0, -4)
            nose_end = self.pos + nose
            pygame.draw.line(screen, (255, 0, 0), nose_start, nose_end, 2)



    class Ship:

        def __init__(self, x, y):
            self.pos = pygame.math.Vector2(x, y)
            self.speed = 4
            self.rotation = 0
            self.velocity = pygame.math.Vector2(0, -0.5)
            self.acceleration = 0.1
            self.thrusting = False

        def move(self, keys):
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rotation -= 5
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rotation += 5

            self.thrusting = keys[pygame.K_UP] or keys[pygame.K_w]
            if self.thrusting:
                thrust = pygame.math.Vector2(0, -self.acceleration).rotate(self.rotation)
                self.velocity += thrust
                if self.velocity.length() > self.speed:
                    self.velocity.scale_to_length(self.speed)
            else:
                self.velocity = self.velocity * 0.97

            self.pos += self.velocity
            padding = 28

            if self.pos.x < padding or self.pos.x > w - padding:
                self.pos.x = max(padding, min(w - padding, self.pos.x))
                self.velocity.x = 0

            if self.pos.y < padding or self.pos.y > h - padding:
                self.pos.y = max(padding, min(h - padding, self.pos.y))
                self.velocity.y = 0

        def draw(self):

            if self.thrusting:
                flame_points = [
                    pygame.Vector2(0, 24),
                    pygame.Vector2(-7, 9),
                    pygame.Vector2(7, 9),
                ]
                flame_points = [
                    (int(self.pos.x + point.rotate(self.rotation).x), int(self.pos.y + point.rotate(self.rotation).y))
                    for point in flame_points
                ]
                pygame.draw.polygon(screen, (255, 120, 30), flame_points)

            points = [
                pygame.Vector2(0, -22),
                pygame.Vector2(-17, 10),
                pygame.Vector2(17, 10),
            ]
            points = [(int(self.pos.x + p.rotate(self.rotation).x), int(self.pos.y + p.rotate(self.rotation).y)) for p in points]
            pygame.draw.polygon(screen, (255, 255, 255), points, 2)

            nose = pygame.Vector2(0, -28).rotate(self.rotation)
            nose_start = self.pos + pygame.Vector2(0, -4)
            nose_end = self.pos + nose
            pygame.draw.line(screen, (255, 0, 0), nose_start, nose_end, 2)
            
    M_speed = 6
    class Missile:

        def __init__(self, position, target, owner):
            self.pos = pygame.math.Vector2(position)
            self.owner = owner
            direction = pygame.Vector2(target) - self.pos
            self.vel = direction.normalize() * M_speed if direction.length_squared() > 0 else pygame.Vector2()

        def move(self):
            self.pos += self.vel

        def is_on_screen(self):
            return 0 <= self.pos.x <= w and 0 <= self.pos.y <= h

        def draw(self):
            pygame.draw.circle(screen, (255, 220, 80), (int(self.pos.x), int(self.pos.y)), 4)


    class Letter:
        def __init__(self, x, y):
            image_path = os.path.join(os.path.dirname(__file__), "letter.png")
            self.image = pygame.image.load(image_path).convert_alpha()
            image_scale = min(50 / self.image.get_width(), 30 / self.image.get_height())
            image_size = (
                int(self.image.get_width() * image_scale),
                int(self.image.get_height() * image_scale),
            )
            self.image = pygame.transform.smoothscale(self.image, image_size)
            self.rect = self.image.get_rect(center=(x, y))

        def draw(self):
            screen.blit(self.image, self.rect)


    ship = Ship(30, 30)
    missiles = []
    enemy = Enemy(w / 2, h / 2)
    letter = Letter(w - 80, h - 80)

    running = True

    p = 0
    result = None

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        enemy.move(ship)
        keys = pygame.key.get_pressed()
        ship.move(keys)

        if ship.pos.distance_to(letter.rect.center) < 40:
            p += 1
            if p >= 10:
                result = "win"
                running = False
            else:
                letter.rect.center = (
                    random.randint(50, w - 50),
                    random.randint(50, h - 50),
                )


        now = pygame.time.get_ticks()

        for missile in missiles:
            missile.move()

        remaining_missiles = []
        for missile in missiles:
            hit_circle = None
            if missile.owner == "enemy" and missile.pos.distance_to(ship.pos) <= 21:
                result = "lost"
                running = False
            elif missile.is_on_screen():
                remaining_missiles.append(missile)

        missiles = remaining_missiles

        screen.fill((20, 24, 40))
        time_text = font.render(f"Points: {p}", True, (255, 255, 255))
        screen.blit(time_text, (w - time_text.get_width() - 10, 10))
        enemy.draw()
        letter.draw()

        for missile in missiles:
            missile.draw()

        ship.draw()

        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)
    if result is not None:
        image_path = os.path.join(os.path.dirname(__file__), f"{result}.png")
        result_image = pygame.image.load(image_path).convert()
    scale = min(w / result_image.get_width(), h / result_image.get_height())
    size = (
        int(result_image.get_width() * scale),
        int(result_image.get_height() * scale),
    )
    result_image = pygame.transform.smoothscale(result_image, size)
    result_rect = result_image.get_rect(center=(w // 2, h // 2))

    show_screen = True
    while show_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                show_screen = False

        screen.fill((20, 24, 40))
        screen.blit(result_image, result_rect)
        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())