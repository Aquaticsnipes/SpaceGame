import arcade
import os

#Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Master Blasster: The Game"

#Constants for sprites
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 0.1
PLAYER_JUMP_SPEED = 4

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
        #Variable for the players sprite
        self.player_sprite = None

        #keep track of direction facing for bullets
        self.facing = None
        #audio for bullets
        self.gunshot = None
        #audio for walking
        self.walking = None
        #boolean to keep track of if the character should be walking
        self.walk = None
        #change in time to determine footstep audio playing
        self.sound_distance = None
        self.dontworryaboutthis = None
        #prepate a spot for the physics engine
        self.physics_engine = None

        self.multipress = None

        #set a background color for the window
        arcade.set_background_color(arcade.csscolor.INDIANRED)

    #function for game starting values
    #can be called to restart the game
    def setup(self):

        #initialize sprite lists with arcades built in SpriteList class
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.objective_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList() 
        self.gunshot = arcade.sound.load_sound("sprites/audio/sadpew.wav")
        self.walking = arcade.sound.load_sound("sprites/audio/softerstep.wav")
        self.dontworryaboutthis = arcade.load_sound("sprites/audio/fart.wav")
        self.current_song = arcade.load_sound("sprites/audio/EndlessQuiet.wav")
        arcade.play_sound(self.current_song)
        self.sound_distance = 0
        self.walk = False
        self.multipress = False
        #Set up the player
        self.facing = "right"
        self.player_sprite = arcade.AnimatedWalkingSprite()
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 136
        self.player_list.append(self.player_sprite)

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

        #Create the groud
        ground = arcade.Sprite("sprites/environ/marsDirt.png", TILE_SCALING)
        ground.center_x = SCREEN_WIDTH/4
        ground.center_y = 32
        self.wall_list.append(ground)
        ground = arcade.Sprite("sprites/environ/marsDirt.png", TILE_SCALING)
        ground.center_x = 3*(SCREEN_WIDTH/4)
        ground.center_y = 32
        self.wall_list.append(ground)
        ground = arcade.Sprite("sprites/environ/marsDirt.png", TILE_SCALING)
        ground.center_x = 3*(SCREEN_WIDTH/4)
        ground.center_y = 96
        self.wall_list.append(ground)


        #add physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)
    
    #method to handle shooting bullets
    def on_shoot(self):
        
        #print("pew") #debug statement
        #play audio for bullet
        if  ((self.player_sprite._get_texture() in self.player_sprite.stand_left_textures or
            self.player_sprite._get_texture() in self.player_sprite.walk_left_textures)
            and  self.facing == "right"):
            arcade.sound.play_sound(self.dontworryaboutthis)
            bullet = arcade.Sprite("sprites/character/gas.png", 0.015)
            #if facing right start at right side of character png and set bullet travel direction
            if(self.facing == "right"):
                bullet.direction = "right"
                bullet.center_x = self.player_sprite.center_x + 23
            else:
                #start left side of character png and set bullet travel direction
                bullet.direction = "left"
                bullet.center_x = self.player_sprite.center_x - 23
            bullet.center_y = self.player_sprite.center_y - 20
        elif ((self.player_sprite._get_texture() in self.player_sprite.stand_right_textures or
            self.player_sprite._get_texture() in self.player_sprite.walk_right_textures)
            and  self.facing == "left"):
            arcade.sound.play_sound(self.dontworryaboutthis)
            bullet = arcade.Sprite("sprites/character/gas.png", 0.015)
            #if facing right start at right side of character png and set bullet travel direction
            if(self.facing == "right"):
                bullet.direction = "right"
                bullet.center_x = self.player_sprite.center_x + 23
            else:
                #start left side of character png and set bullet travel direction
                bullet.direction = "left"
                bullet.center_x = self.player_sprite.center_x - 23
            bullet.center_y = self.player_sprite.center_y - 20
        else:
            arcade.sound.play_sound(self.gunshot)
            bullet = arcade.Sprite("sprites/battle/ammo.png", 1)
            #if facing right start at right side of character png and set bullet travel direction
            if(self.facing == "right"):
                bullet.direction = "right"
                bullet.center_x = self.player_sprite.center_x + 40
            else:
                #start left side of character png and set bullet travel direction
                bullet.direction = "left"
                bullet.center_x = self.player_sprite.center_x - 40
            
            bullet.center_y = self.player_sprite.center_y

        

        self.bullet_list.append(bullet)

    #changes bullets location (acts as the bullets speed)
    def update_bullets(self):
        for bullet in self.bullet_list:
            if bullet.direction == "right":
                bullet.center_x += 12
            else:
                bullet.center_x -= 12

    #get user input
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        #check if physics is active for jumping
        
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                        
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

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        #for each frame add one to time between footstep audio
        self.sound_distance += 1
        #update all sprites
        #print(self.player_sprite._get_texture())
        self.update_bullets()
        self.player_list.update()
        self.player_list.update_animation()
        self.physics_engine.update()
        if self.player_sprite.center_x >= SCREEN_WIDTH:
            self.player_sprite.center_x = 10
        elif self.player_sprite.center_x <= 0:
            self.player_sprite.center_x = SCREEN_WIDTH - 10
        

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
        #code to draw things to on the screen goes here


#main method to initialize the window
def main():
    window = MasterBlaster()
    window.setup()
    arcade.run()


#programs main, only method to run when program executes
if __name__ == "__main__":
    main()
