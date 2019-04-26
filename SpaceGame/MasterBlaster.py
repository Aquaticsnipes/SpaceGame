#created by 
#Adam A and Chris S
import arcade
#import pygame
import os
import random
import time
#Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Master Blaster: The Game"

#Constants for sprites
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 0.1
PLAYER_JUMP_SPEED = 5.5
#ENEMY_BOB_SPEED = 10
HIGH_SCORE = None
BULLET_DAMAGE = 55
TEXTURE_LEFT = 0
TEXTURE_RIGHT = 1
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

#Viewport for player def scroll
LEFT_VEIWPORT_MARGINE = 150
RIGHT_VEIWPORT_MARGINE = 150
BOTTOM_VEIWPORT_MARGINE = 50
TOP_VEIWPORT_MARGINE = 100


class Enemy(arcade.Sprite):

    def __init__(self, h):
        super().__init__()

        # Load a left facing texture and a right facing texture.
        # mirrored=True will mirror the image we load.
        texture = arcade.load_texture("sprites/character/alienFLeft.png", mirrored=False, scale=CHARACTER_SCALING)
        self.textures.append(texture)
        texture = arcade.load_texture("sprites/character/alienFLeft.png", mirrored=True, scale=CHARACTER_SCALING)
        self.textures.append(texture)
        self.health = h
        #This default is overwritten by the travel direction anyways
        self.set_texture(random.randint(0,1))
        

class Player(arcade.AnimatedWalkingSprite):

    def __init__(self, h):
        super().__init__()

        # Load a left facing texture and a right facing texture.
        # mirrored=True will mirror the image we load.
        texture = arcade.load_texture("sprites/character/rFacing.png", mirrored=True, scale=CHARACTER_SCALING)
        self.textures.append(texture)
        texture = arcade.load_texture("sprites/character/rFacing.png", mirrored=False, scale=CHARACTER_SCALING)
        self.textures.append(texture)
        self.health = h
        # By default, face right.
        self.set_texture(TEXTURE_RIGHT)
        

#class to represent the game application
#inherit from arcade.Window
class MasterBlaster(arcade.Window):
    def __init__(self):

        #set the up the window using the super class
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        #Make lists to keep sprites in. All sprites need to go in a list
        self.objective_list = None
        self.wall_list = None
        self.player_list = None
        self.bullet_list = None
        self.sound_track = None
        self.enemy_list = None

        #used to keep track of scrolling
        self.veiw_left = 0
        self.veiw_bottom = 0

        #Variable for the players sprite
        self.player_sprite = None
        self.bob_count = None
        self.firemode = {   
                            0:"semi-auto",
                            1:"burst"
                        }
        self.mode = 0
        #self.timer = 0
        #audio for bullets
        self.gunshot = None
        self.score = None
        #boolean to keep track of if the character should be walking
        self.walk = None
        #change in time to determine footstep audio playing
        self.sound_distance = None
        self.dontworryaboutthis = None
        #prepate a spot for the physics engine
        self.physics_engine = None

        #helper variables

        self.multipress = None
        #boolean to keep track of if the character should be walking
        self.walk = None
        #audio for walking
        self.walking = None
        #keep track of direction facing for bullets
        self.facing = None
        self.current_song = arcade.load_sound("sprites/audio/Endless_quiet.mp3")
        arcade.play_sound(self.current_song)
        #set a background color for the window
        arcade.set_background_color(arcade.csscolor.INDIANRED)

    #function for game starting values
    #can be called to restart the game
    def setup(self):

        #initialize sprite lists with arcades built in SpriteList class
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.objective_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList() 
        self.gunshot = arcade.sound.load_sound("sprites/audio/sadpew.wav")
        self.walking = arcade.sound.load_sound("sprites/audio/softerstep.wav")
        
        self.enemy_hit = arcade.load_sound("sprites/audio/hit.wav")
        self.hurt = arcade.load_sound("sprites/audio/oww.wav")
        self.canHurt = 0
        self.score = 0

        self.sound_distance = 0
        self.bob_count = 0
        self.walk = False
        self.multipress = False
        #Set up the player
        self.facing = "right"
        self.player_sprite = Player(100)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 200
        self.player_list.append(self.player_sprite)

        #Arrays of Player textures to used by the arcade.AnimatedWalkingSprite class
        self.player_sprite.stand_right_textures = []
        self.player_sprite.stand_right_textures.append(arcade.load_texture("sprites/character/rFacing.png",
                                                                    scale=CHARACTER_SCALING))
        self.player_sprite.stand_left_textures = []
        self.player_sprite.stand_left_textures.append(arcade.load_texture("sprites/character/rFacing.png",
                                                                   scale=CHARACTER_SCALING, mirrored=True))

        self.player_sprite.walk_right_textures = []

        self.player_sprite.walk_right_textures.append(arcade.load_texture("sprites/character/rFacing.png",
                                                                   scale=CHARACTER_SCALING))
        self.player_sprite.walk_right_textures.append(arcade.load_texture("sprites/character/rWalking.png",
                                                                   scale=CHARACTER_SCALING))


        self.player_sprite.walk_left_textures = []

        self.player_sprite.walk_left_textures.append(arcade.load_texture("sprites/character/rFacing.png",
                                                                  scale=CHARACTER_SCALING, mirrored=True))
        self.player_sprite.walk_left_textures.append(arcade.load_texture("sprites/character/rWalking.png",
                                                                  scale=CHARACTER_SCALING, mirrored=True))

        self.player_sprite.texture_change_distance = 48

        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = "sprites/environ/MASTER_BLASTER_MAP.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Tile Layer 1'
        

        # Read in the tiled map
        my_map = arcade.read_tiled_map(map_name, TILE_SCALING)

        # -- Walls
        # Grab the layer of items we can't move through
        map_array = my_map.layers_int_data[platforms_layer_name]

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE

        # -- Platforms
        self.wall_list = arcade.generate_sprites(my_map, platforms_layer_name, TILE_SCALING)

        # --- Other stuff
        # Set the background color
        if my_map.backgroundcolor:
            arcade.set_background_color(my_map.backgroundcolor)


        #add physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)
    
    #method to handle shooting bullets
    def on_shoot(self):
        
        #print("pew") #debug statement
        #play audio for bullet

        arcade.sound.play_sound(self.gunshot)
        bullet = arcade.Sprite("sprites/battle/ammo.png", 1)
        #if facing right start at right side of character png and set bullet travel direction
        if (self.player_sprite._get_texture() in self.player_sprite.stand_right_textures or
        self.player_sprite._get_texture() in self.player_sprite.walk_right_textures):
            bullet.direction = "right"
            bullet.center_x = self.player_sprite.center_x + 40
        else:
            #start left side of character png and set bullet travel direction
            bullet.direction = "left"
            bullet.center_x = self.player_sprite.center_x - 40
        bullet.start_x = bullet.center_x
        bullet.center_y = self.player_sprite.center_y
        self.bullet_list.append(bullet)

    #pick if enemies should spawn, then create enemy sprite if necessary
    def enemy_spawner(self):
        if len(self.enemy_list) < 3 and random.randint(1,100) < 3:
            newEn = Enemy(150)
            newEn.center_x = random.randint(int(self.veiw_left + 50) , int(self.veiw_left + (SCREEN_WIDTH -50)))
            newEn.center_y = random.randint(int(self.veiw_bottom + 200) , int(self.veiw_bottom + (SCREEN_HEIGHT - 50)))
            self.enemy_list.append(newEn)
            self.player_list.append(newEn)

    #changes bullets location (acts as the bullets speed)
    def update_bullets(self):
        for bullet in self.bullet_list:
            if bullet.direction == "right":
                bullet.center_x += 12
            else:
                bullet.center_x -= 12
            if bullet.center_x < self.player_sprite.center_x - 1280 or bullet.center_x > self.player_sprite.center_x + 1280:
                bullet.remove_from_sprite_lists()

    #for weapon select fire mode (future implementation)
    def switch_firemode(self):
        if self.mode == 0:
            self.mode = 1
        elif self.mode == 1:
            self.mode = 0

    #get user input
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        #check if physics is active for jumping
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        
        #handle player input
        if key == arcade.key.LEFT or key == arcade.key.A:
            if(self.player_sprite.change_x is not 0):
                self.player_sprite.change_x = 0
                self.multipress = True
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.facing = "left"
            self.walk = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            if(self.player_sprite.change_x is not 0):
                self.player_sprite.change_x = 0
                self.multipress = True
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.facing = "right"
            self.walk = True
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            #call shoot method
            self.on_shoot()
        #elif key == arcade.key.V:
        #    self.switch_firemode()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if self.multipress == True:
            self.multipress = False
        else:
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.player_sprite.change_x = 0
                self.walk = False
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.walk = False
                self.player_sprite.change_x = 0
                

    def update(self, delta_time):
        """ Movement and game logic """
        global HIGH_SCORE
        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        #for each frame add one to time between footstep audio
        self.sound_distance += 1
        self.bob_count += 1
        self.canHurt += 1
        #self.timer += 1
        #update all sprites
        #print(self.player_sprite._get_texture())
        self.update_bullets()
        self.player_list.update()
        self.player_list.update_animation()
        self.physics_engine.update()
        #if self.bob_count > ENEMY_BOB_SPEED:
        #    self.enemy_list.update()

        changed = False

        #scroll LEFT
        left_boundry = self.veiw_left + LEFT_VEIWPORT_MARGINE
        if self.player_sprite.left < left_boundry:
        	self.veiw_left -= left_boundry - self.player_sprite.left
        	changed = True

        #scroll RIGHT
        right_boundry = self.veiw_left + SCREEN_WIDTH - RIGHT_VEIWPORT_MARGINE
        if self.player_sprite.right > right_boundry:
        	self.veiw_left += self.player_sprite.right - right_boundry
        	changed = True

        #scroll UP
        top_boundry = self.veiw_bottom + SCREEN_HEIGHT - TOP_VEIWPORT_MARGINE
        if self.player_sprite.top > top_boundry:
        	self.veiw_bottom += self.player_sprite.top - top_boundry
        	changed = True

        #scroll DOWN
        bottom_boundry = self.veiw_bottom + BOTTOM_VEIWPORT_MARGINE
        if self.player_sprite.bottom < bottom_boundry:
        	self.veiw_bottom -= bottom_boundry - self.player_sprite.bottom
        	changed = True

        #scroll action
        if changed:
        	self.veiw_left = int(self.veiw_left)
        	self.bottom = int(self.veiw_bottom)
        	arcade.set_viewport(self.veiw_left, SCREEN_WIDTH + self.veiw_left, self.veiw_bottom, SCREEN_HEIGHT + self.veiw_bottom)

        #boundry checking for player to stay on the map
        if self.player_sprite.center_x >= 5766:
            self.player_sprite.center_x = 75
            self.player_sprite.center_y = 200
        elif self.player_sprite.center_x <= 62:
            self.player_sprite.center_x = 5750
            self.player_sprite.center_y = 840
        if self.player_sprite.center_y <= 0:
            self.player_sprite.center_x = 64
            self.player_sprite.center_y = 200

        #loop through list of enemies
        for alien in self.enemy_list:

            #first check to see if aliens are 150 picels or further off any side of the screen
            #if so remove them
            if alien.center_x < self.veiw_left - 150 or alien.center_x > self.veiw_left + SCREEN_WIDTH + 150:
                alien.remove_from_sprite_lists()
            elif alien.center_y < self.veiw_bottom - 150 or alien.center_y > self.veiw_bottom + SCREEN_HEIGHT+ 150:
                alien.remove_from_sprite_lists()
            else:
                #determine movement for enemies
                #currently a direct path towards player 
                if alien.center_x > self.player_sprite.center_x + 1:
                    alien.change_x = -1
                    alien.set_texture(TEXTURE_LEFT)
                elif alien.center_x < self.player_sprite.center_x - 1:
                    alien.change_x = 1
                    alien.set_texture(TEXTURE_RIGHT)
                else:
                    alien.set_texture(TEXTURE_RIGHT)
                
                if alien.center_y > self.player_sprite.center_y:
                    alien.change_y = -0.7
                elif alien.center_y < self.player_sprite.center_y:
                    alien.change_y = 0.7
        
        #check if player touches an enemy
        if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list):
            #one damage to player per frame that the model is touching the enemy
            self.player_sprite.health -= 0.5
            if self.canHurt > 20:
                #only play audio for getting hurt every 20 frames.
                #about every 1/3 of a second
                arcade.sound.play_sound(self.hurt)
                self.canHurt = 0
            #if players health falls below 0, start a new round
            if self.player_sprite.health <= 0:
                self.player_sprite.remove_from_sprite_lists()
                self.setup()

        #keep track of high score
        if self.score > HIGH_SCORE:
            HIGH_SCORE = self.score

        #call method to spawn enemies if necessary
        self.enemy_spawner()

        #check all the bullets in the list
        for bullet in self.bullet_list:
            #if bullet hits a wall get rid of the bullet
            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()
            else:
                #check the bullet against each enemy
                for enemy in self.enemy_list:
                    if arcade.check_for_collision(bullet, enemy):
                        arcade.play_sound(self.enemy_hit)
                        #damage fallow, subtracts 5% damage reduced per pixel travelled
                        dmg = BULLET_DAMAGE - (abs(bullet.start_x - bullet.center_x) * 0.05)

                        if dmg < 0:
                            dmg = 0
                        
                        #get rid of bullet on impact with enemy
                        bullet.remove_from_sprite_lists()
                        #deal damage to enemy
                        enemy.health -= dmg
                    #if the enemies health falls below 0 get rid of the enemy
                    #add 10 points to players score
                    if enemy.health <= 0:
                        enemy.remove_from_sprite_lists()
                        self.score += 10
        

    #render screen
    def on_draw(self):
        arcade.start_render()
        
        #if 1/4 second between audio for footsteps and player is walking
        if self.sound_distance > 15 and self.walk:
            #play footstep sound
            arcade.sound.play_sound(self.walking)
            self.sound_distance = 0
        #print(self.sound_distance) #debug statement
        self.bullet_list.draw()
        self.player_list.draw()
        self.wall_list.draw()
        self.enemy_list.draw()
        #code to draw things to on the screen goes here
        
        #print(self.player_sprite.center_x, self.player_sprite.center_y)

        #Output for any text that needs to be displayed to the game
        output = f"High Score : {HIGH_SCORE}"
        arcade.draw_text(output, self.veiw_left + 10, self.veiw_bottom + (SCREEN_HEIGHT - 20), arcade.color.WHITE, 16)
        output = f"Current Score : {self.score}"
        arcade.draw_text(output, self.veiw_left + 10, self.veiw_bottom + (SCREEN_HEIGHT - 40), arcade.color.WHITE, 16)
        #output = f"Fire Mode : {self.firemode[self.mode]}"
        #arcade.draw_text(output, 10, 40, arcade.color.WHITE, 16)
        output = f"{self.player_sprite.health:.3g}%"
        arcade.draw_text(output, self.player_sprite.center_x - 25, self.player_sprite._get_top() + 2, arcade.color.WHITE, 16)


#main method to initialize the window
def main(): 

    #read in high score from save file,
    #or set high score to 0 if no save data available
    global HIGH_SCORE
    try:
        file = open("save.txt", "r")

        if os.stat("save.txt").st_size == 0:
            HIGH_SCORE = 0
        else:
            HIGH_SCORE = int(file.read())
    except:
        file = open("save.txt", "w")
        file.write("0")
        HIGH_SCORE = 0
    file.close()
    
    #run the game
    window = MasterBlaster()
    window.setup()
    arcade.run()

    #save the high score to the file when the game ends
    file = open("save.txt", "w")
    file.write(str(HIGH_SCORE))
    window.close()


#programs main, only method to run when program executes
if __name__ == "__main__":
    main()