import pygame
import random
import json
from pygame.locals import *
from pygame import mixer
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)

mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

#NOTE grid is 51 * 27 
screen_width = 1275
screen_hight = 675

screen = pygame.display.set_mode((screen_width, screen_hight), pygame.FULLSCREEN)
pygame.display.set_caption("game")

tile_size = 25
game_over = 0
menu = False
main_menu = True
level = 1
max_levels = 3

#load and scale images
background1_img = pygame.image.load('images/background1.png').convert()
background2_img = pygame.image.load('images/background2.png').convert()
background3_img = pygame.image.load('images/background3.png').convert()
background4_img = pygame.image.load('images/background4.png').convert()

background_img = [background1_img, background2_img, background3_img, background4_img]

restart_button_img = pygame.image.load('images/restart.png')
restart_button_img = pygame.transform.scale(restart_button_img, (100, 50))
main_menu_button_img = pygame.image.load('images/mainmenu.png')
main_menu_button_img = pygame.transform.scale(main_menu_button_img, (100, 50))
game_over_button_img = pygame.image.load('images/gameover.png')
game_over_button_img = pygame.transform.scale(game_over_button_img, (800, 150))

start_img = pygame.image.load('images/start.png')
start_img = pygame.transform.scale(start_img, (100, 50))
quit_img = pygame.image.load('images/quit.png')
quit_img = pygame.transform.scale(quit_img, (100, 50))

#load sound
woo1 = pygame.mixer.Sound('sounds/woo1.mp3')
woo2 = pygame.mixer.Sound('sounds/woo2.mp3')
woo3 = pygame.mixer.Sound('sounds/woo3.mp3')
woo4 = pygame.mixer.Sound('sounds/woo4.mp3')
woo5 = pygame.mixer.Sound('sounds/woo5.mp3')
woo6 = pygame.mixer.Sound('sounds/woo6.mp3')
jump_list = [woo1]

pygame.mixer.music.load('sounds/music1.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)


spring_noise = pygame.mixer.Sound('sounds/boing.mp3')
spring_noise.set_volume(0.5)
victory_noise = pygame.mixer.Sound('sounds/victorynoise.mp3')
victory_noise.set_volume(0.5)
scribble = pygame.mixer.Sound('sounds/scribble.mp3')
scribble.set_volume(10)



#reset level function
def reset_level(level):
    player.reset(50, screen_hight - 50)
    crayon_group.empty()
    pencil_group.empty()
    spikes_group.empty()
    spikesu_group.empty()
    flag_group.empty()
    platformh_group.empty()
    platformv_group.empty()
    spring_group.empty()
    if level > 1:
        pygame.mixer.music.stop()
    pygame.mixer.music.load(f'sounds/music{level}.mp3')
    pygame.mixer.music.play(-1, 0.0, 5000)
    #background_img = pygame.image.load(f'images/background{level}.png')
    
    
    if path.exists(f'level{level}.txt'):
        level_file = open(f'level{level}.txt', 'r')
        world_data = json.load(level_file)
    world = World(world_data)
    
    return world
    

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    
    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                scribble.play()
                self.clicked = True
                
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        screen.blit(self.image, self.rect)
        return action
    
    




class Player():
    def __init__(self, x, y):
        
        self.reset(x, y)
        
    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20
        
        
        
        if game_over == 0:
        
        
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                self.vel_y = -8
                jump_sound = random.choice(jump_list)
                jump_sound.play()
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 3
                self.counter += 1
                self.direction = -1
            if key[pygame.K_d]:
                dx += 3
                self.counter += 1
                self.direction = 1
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index]
            
            
            #handle anim
            
            if self.counter > walk_cooldown:
                self.counter = 1
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 1
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
                    
            
            
            
            
            self.vel_y += 0.5
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y
            
            #check for colission
            self.in_air = True
            for tile in world.tile_list:
                #check x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.hight):
                    dx = 0
                #check y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.hight):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        #self.vel_y = 0
                        self.in_air = False
            
            
            if pygame.sprite.spritecollide(self, crayon_group, False):
                game_over = -1
                woo2.play()
                
            if pygame.sprite.spritecollide(self, pencil_group, False):
                game_over = -1
                woo2.play()
            
            if pygame.sprite.spritecollide(self, spikes_group, False):
                game_over = -1
                woo2.play()
                
            if pygame.sprite.spritecollide(self, spikesu_group, False):
                game_over = -1
                woo2.play()
            
            if pygame.sprite.spritecollide(self, flag_group, False):
                game_over = 1
                victory_noise.play()
            
            if pygame.sprite.spritecollide(self, spring_group, False):
                self.vel_y = -14
                spring_noise.play()
                
            
            for platform in platformh_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.hight):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.hight):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs(self.rect.bottom + dy - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
                    self.rect.x += platform.direction
                    
                    
            for platform in platformv_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.hight):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.hight):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs(self.rect.bottom + dy - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
            
            
            
            #check player coordinated
            self.rect.x += dx
            self.rect.y += dy
            
            #temporary for bottom of screen check
            #if self.rect.bottom > screen_hight:
            #    self.rect.bottom = screen_hight
            #    dy = 0
        elif game_over == -1:
            self.image = self.dead_image
            #self.rect.y += 3
            
        screen.blit(self.image, self.rect)
        return game_over
        
        
        
    def reset(self, x, y):
    
        self.images_right = []
        self.images_left = []
        
        self.index = 0
        self.counter = 0
        for num in range(1, 8):
            img = pygame.image.load(f'images/player{num}.png')
            img_right = pygame.transform.scale(img, (20, 40))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('images/dead.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (20, 40))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.hight = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True
    

class World():
    def __init__(self, data):
        self.tile_list = []
        
        
        #load images
        block1_img = pygame.image.load('images/block11.png')
        block2_img = pygame.image.load('images/block22.png')
        block3_img = pygame.image.load('images/block33.png')
        block4_img = pygame.image.load('images/block44.png')
        block_list = [block1_img, block2_img, block3_img, block4_img]
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(random.choice(block_list), (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    crayon = Enemy(col_count * tile_size, row_count * tile_size - 10)
                    crayon_group.add(crayon)
                if tile == 3:
                    spikes = Spikes(col_count * tile_size, row_count * tile_size + 12)
                    spikes_group.add(spikes)
                if tile == 4:
                    spikesu = Spikesu(col_count * tile_size, row_count * tile_size - 2)
                    spikesu_group.add(spikesu)
                if tile == 5:
                    platformv = Platformv(col_count * tile_size, row_count * tile_size)
                    platformv_group.add(platformv)
                if tile == 6:
                    platformh = Platformh(col_count * tile_size, row_count * tile_size)
                    platformh_group.add(platformh)
                if tile == 7:
                    flag = Flag(col_count * tile_size - 10, row_count * tile_size - 25)
                    flag_group.add(flag)
                if tile == 8:
                    pencil = Enemyh(col_count * tile_size, row_count * tile_size - 3)
                    pencil_group.add(pencil)
                if tile == 9:
                    spring = Spring(col_count * tile_size, row_count * tile_size + 12)
                    spring_group.add(spring)
                col_count += 1
            row_count += 1
            
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            
            
   

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/enemy3.png')
        self.image = pygame.transform.scale(self.image, (17, 34))
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.counter = 0
        
    def update(self):
        self.rect.x += self.direction
        self.counter += 1
        if abs(self.counter) > 100:
            self.direction *= -1
            self.counter *= -1
            self.image = pygame.transform.flip(self.image, True, False)
            
class Enemyh(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/pencil.png')
        self.image = pygame.transform.scale(self.image, (50, 25))
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.counter = 0
        
    def update(self):
        self.rect.x += self.direction
        self.counter += 1
        if abs(self.counter) > 125:
            self.direction *= -1
            self.counter *= -1
            self.image = pygame.transform.flip(self.image, True, False)

class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/spikes.png')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
class Spikesu(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/spikes.png')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.image = pygame.transform.flip(self.image, False, True)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
  
class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/flag.png')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size * 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Platformh(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/platformh.png')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.counter = 0
        self.direction = -1
        
    def update(self):
        self.rect.x += self.direction
        self.counter += 1
        if abs(self.counter) > 75:
            self.direction *= -1
            self.counter *= -1
 

class Platformv(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/platformv.png')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.counter = 0
        self.direction = -1
        
    def update(self):
        self.rect.y += self.direction
        self.counter += 1
        if abs(self.counter) > 75:
            self.direction *= -1
            self.counter *= -1 
 
class Spring(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/spring.png')
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
 
        
#groups
player = Player(50, screen_hight - 50)
platformh_group = pygame.sprite.Group()
platformv_group = pygame.sprite.Group()
crayon_group = pygame.sprite.Group()
pencil_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
spikesu_group = pygame.sprite.Group()
flag_group = pygame.sprite.Group()
spring_group = pygame.sprite.Group()


#if path.exists(f'level{level}'):
#    pickle_in = open(f'level{level}', 'rb')
 #   world_data = pickle.load(pickle_in)
if path.exists(f'level{level}.txt'):
    level_file = open(f'level{level}.txt', 'r')
    world_data = json.load(level_file)
world = World(world_data)




#buttons
game_over_button = Button(screen_width // 2 - 400, screen_hight // 2 - 200, game_over_button_img)
restart_button = Button(screen_width // 2 - 50, screen_hight // 2, restart_button_img)
start_button = Button(screen_width // 2 - 200, screen_hight // 2 - 100, start_img)
quit_button = Button(screen_width // 2 + 100, screen_hight // 2 - 100, quit_img)
main_menu_button = Button(screen_width // 2 - 50, screen_hight // 2 - 100, main_menu_button_img)









run = True
while run == True:

    clock.tick(fps)


    screen.blit(background_img[level - 1], (0, 0))

    if main_menu == True:
        if start_button.draw():
            main_menu = False
        if quit_button.draw():
            run = False
    else:
        world.draw()
        
        if game_over == 0:
            crayon_group.update()
            pencil_group.update()
            platformh_group.update()
            platformv_group.update()
            
        
        platformh_group.draw(screen)
        
        platformv_group.draw(screen)
        
        crayon_group.draw(screen)
        
        pencil_group.draw(screen)
        
        spikes_group.draw(screen)
        
        spikesu_group.draw(screen)
        
        flag_group.draw(screen)
        
        spring_group.draw(screen)
        
        game_over = player.update(game_over)
        
        key = pygame.key.get_pressed()
        if (key[pygame.K_ESCAPE] and menu == False) or menu == True:
            menu = True
            if main_menu_button.draw():
                level = 1
                world_data = []
                world = reset_level(level)
                game_over = 0
                main_menu = True
                menu = False
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                menu = False
        
            
        
        if game_over == -1:
            game_over_button.draw()
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

                
        if game_over == 1:
            
            if level < max_levels:
                level += 1
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                if main_menu_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    main_menu = True
                
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    pygame.display.update()
            
pygame.quit()