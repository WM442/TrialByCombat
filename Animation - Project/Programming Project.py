import pygame
import sqlite3
pygame.init()

#Create a database
database = sqlite3.connect('game_data.db')
cursor = database.cursor()

#Create a table for amount of rounds played
cursor.execute('''
    CREATE TABLE IF NOT EXISTS roundsPlayed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
       total_rounds INTEGER NOT NULL
    )
''')

#Insert and update values in database
cursor.execute('SELECT total_rounds FROM roundsPlayed WHERE id=1')
if cursor.fetchone() is None:
    cursor.execute('INSERT INTO roundsPlayed (total_rounds) VALUES (0)')
    database.commit()

#Funcion to increment total rounds oncea round is over
def increment_rounds():
    cursor.execute('UPDATE roundsPlayed SET total_rounds = total_rounds + 1 WHERE id=1')
    database.commit()

#Extract the total rounds to be displayed on the screen
def get_total_rounds():
    cursor.execute('SELECT total_rounds FROM roundsPlayed WHERE id=1')
    return cursor.fetchone()[0]

# Constants
WIDTH, HEIGHT = 820, 400
gravity = 12
font = pygame.font.SysFont("comicsans", 20, True)

# Initialize window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trial by Combat")

# Load assets
walkRight = [pygame.image.load(f'R{i}.png') for i in range(1, 10)]
walkLeft = [pygame.image.load(f'L{i}.png') for i in range(1, 10)]
char = pygame.image.load('standing.png')

walkLeft2 = [pygame.image.load(f'L{i}A3.png') for i in range(1, 10)]
walkRight2 = [pygame.image.load(f'L{i}A3.png') for i in range(1, 10)]
dragon = pygame.image.load('L1A3.png')

bg = pygame.image.load('bg4.jpg')

#Creating a class called Player, with all variables/attributes required inside of it
class Player: 
    def __init__(self, x, y, width, height, speed, images_right, images_left, idle_image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.left = False
        self.right = False
        self.jump_status = False
        self.jump_time = 10
        self.anim_num = 0
        self.images_right = images_right
        self.images_left = images_left
        self.idle_image = idle_image
        self.hitbox = (self.x + 17, self.y + 11, 29, 52)
        self.health = 10
        self.visible = True
        self.maxhealth = 10
        self.score = 0
        self.start = (x,y)
        self.start_x = 200
        self.start_y = 317
        self.start_x1 = 500
        self.start_y1 = 285
        
#Used to reset the game once player's health < 0        
    def reset(self):
        player1.x = self.start_x
        player1.y = self.start_y
        player2.x = self.start_x1
        player2.y = self.start_y1
        self.health = self.maxhealth
        self.visible = True
        
        
#Detects when a player's health is < 0 and increments each player's score 
    def hit(self):
        if self.health > 0:
            self.health -= 1
        else:
            self.visible = False
            if self == player1 and player2.health > 0:
                player2.score += 1
                self.reset()
                player2.reset()
                increment_rounds()
            elif self == player2 and player1.health > 0:
                player1.score += 1
                self.reset()
                player1.reset()
                increment_rounds()
            elif player1.health == player2.health:
                player1.score += 1
                player2.score += 1
                self.reset()
                increment_rounds()
        print('hit')

        
        
#Movement to allow the player to move across the screen
    def move(self, keys, left_key, right_key, jump_key):
        if keys[left_key] and self.x > self.speed:
            self.x -= self.speed
            self.left, self.right = True, False
        elif keys[right_key] and self.x < WIDTH - self.width - self.speed:
            self.x += self.speed
            self.left, self.right = False, True
        else:
            self.left = self.right = False
            self.anim_num = 0

        if not self.jump_status and keys[jump_key]:
            self.jump_status = True
            self.left = self.right = False
            self.anim_num = 0
        elif self.jump_status:
            acceleration = 1 if self.jump_time >= 0 else -1
            self.y -= (self.jump_time ** 2) * 0.4 * acceleration
            self.jump_time -= 1
            if self.jump_time < -10:
                self.jump_status = False
                self.jump_time = 10

#Implementing gravity for all players
    def apply_gravity(self, platforms, floor_y):
        if not self.jump_status and not any(p.colliderect(self.get_rect()) for p in platforms) and self.y < floor_y:
            self.y += gravity
        if self.y > floor_y:
            self.y = floor_y
        for platform in platforms:
            if platform.colliderect(self.get_rect()) and self.y + self.height > platform.top > self.y:
                self.y = platform.top - self.height

#Creating rectangles on the screen
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

#Drawing all player images, rectangles, hitboxes, and writing on the screen
    def draw(self, win):
        if self.visible:
            if self.anim_num + 1 >= 27:
                self.anim_num = 0
            if self.left:
                win.blit(self.images_left[self.anim_num // 3], (self.x, self.y))
            elif self.right:
                win.blit(self.images_right[self.anim_num // 3], (self.x, self.y))
            else:
                win.blit(self.idle_image, (self.x, self.y))
            self.anim_num += 1
        
        self.hitbox = (self.x + 17, self.y + 11, 29, 52)
        pygame.draw.rect(win, (255,0,0), (self.hitbox[0], self.hitbox[1] - 20, 50, 10))
        pygame.draw.rect(win, (0,128,0), (self.hitbox[0], self.hitbox[1] - 20, 50 - (5 * (10 - self.health)), 10))
        text = font.render("P1 Score: " + str(player1.score), 1, (0,0,0))
        win.blit(text, (30, 10))
        text2 = font.render("P2 Score: " + str(player2.score), 1, (0,0,0))
        win.blit(text2, (500,10))
        rounds_text = font.render("Total Rounds: " + str(get_total_rounds()), 1, (0,0,0))
        win.blit(rounds_text, (250, 10))

#Drawing the platforms
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), self.rect)

#Creating a class called projectile, with attributes below it
class Projectile:
    def __init__(self, x, y, radius, color, speed, direction, shooter):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed * direction * 1.3
        self.active = True
        self.shooter = shooter

#Controlling speed of projectiles
    def move(self):
        self.x += (self.speed)
        if self.x > WIDTH or self.x < 0:
            self.active = False

#Drawing the projectiles on the screen
    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)
        

# Initialize players
player1 = Player(200, 317, 64, 64, 10, walkRight, walkLeft, char)
player2 = Player(500, 285, 92, 85, 10, walkRight2, walkLeft2, dragon)

# Platforms
platforms = [
    Platform(275, 250, 120, 10),
    Platform(75, 125, 80, 10),
    Platform(470, 110, 70, 10),
    Platform(650, 220, 95, 10)
]

# Projectiles
bullets = []
shootLoop1 = 0
shootLoop2 = 0 

# Game loop
clock = pygame.time.Clock()
run = True
while run:
    clock.tick(27)
    
#Creates a loop which ensures that each bullet has a time delay before another one can be shot
    if shootLoop1 > 0:
        shootLoop1 += 1
    if shootLoop1 > 5:
        shootLoop1 = 0
        
    if shootLoop2 > 0:
        shootLoop2 += 1
    if shootLoop2 > 5:
        shootLoop2 = 0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    for bullet in bullets:
        for player in [player1, player2]:  # Check collision for both players
            if (bullet.y - bullet.radius < player.hitbox[1] + player.hitbox[3] and 
                bullet.y + bullet.radius > player.hitbox[1] and 
                bullet.x + bullet.radius > player.hitbox[0] and 
                bullet.x - bullet.radius < player.hitbox[0] + player.hitbox[2]):

            # Ensure the bullet doesn't hit the player who fired it
                if bullet.shooter == player:
                     continue  # Skip if the bullet belongs to the player

                player.hit()  # Call the hit method on the instance
                bullets.pop(bullets.index(bullet))
                break  # Exit loop once a bullet hits a player
                

              
    keys = pygame.key.get_pressed()
    player1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w)
    player2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
    player1.apply_gravity([p.rect for p in platforms], 317)
    player2.apply_gravity([p.rect for p in platforms], 285)

#Allow for users to press space and end buttons to shoot
    if keys[pygame.K_SPACE] and shootLoop1 == 0:
        direction = -1 if player1.left else 1
        spawn_x = player1.x + 25 if direction == -1 else player1.x + (player1.width // 2)
        bullets.append(Projectile(spawn_x, player1.y + player1.height // 2, 5, (255, 255, 0), 10, direction, player1))
        shootLoop1 = 1
    
    if keys[pygame.K_END] and shootLoop2 == 0:
        direction = 1 if player2.right else -1
        bullets.append(Projectile(player2.x + player2.width // 2, player2.y + player2.height // 2, 5, (0, 255, 0), 10, direction, player2))
        shootLoop2 = 1
        
    for bullet in bullets:
        bullet.move()
    bullets = [bullet for bullet in bullets if bullet.active]

#Updating screen to allow for classes/objects to load in and refresh once as they move
    win.blit(bg, (0, 0))
    for platform in platforms:
        platform.draw(win)
    player1.draw(win)
    player2.draw(win)
    for bullet in bullets:
        bullet.draw(win)
    pygame.display.update()

pygame.quit()
database.close()

