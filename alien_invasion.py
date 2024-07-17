import sys
from time import sleep
from settings import Settings
from ship import Ship
import pygame
from bullet import Bullet
from alien import Alien
from game_stats import Gamestats
from button import Button
from scoreboard import Scoreboard
from pathlib import Path

class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.game_active = False
        self.clock = pygame.time.Clock()
        self.settings=Settings()                                    #(0,0),pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        self.ship = Ship(self) #这里的self是AlienInvasion以供Ship类能访问游戏里的资源，如：screen.....
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        self.stats = Gamestats(self)
        self.play_button =Button(self,"Play")
        self.sb = Scoreboard(self) 



    def run_game(self):
        while True :   
            self._check_events()
            
            if self.game_active:
               self.ship.update()
               self._update_bullets_()
               self._update_aliens()            
            self._update_screen()
            self.clock.tick(60)
  
    
    def _check_events(self): 
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                self._write_high_score()
                sys.exit()         
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_buttom(mouse_pos)


    def _check_play_buttom(self,mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self._start_game()


    def _start_game(self):
        self.stats.reset_stats()
        self.game_active = True

        self.bullets.empty()
        self.aliens.empty()

        self._create_fleet()
        self.ship.center_ship()

        pygame.mouse.set_visible(False)
        self.settings.initialize_dynamic_settings()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

                 
    def _check_keydown_events(self,event):
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = True
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = True
            elif event.key == pygame.K_SPACE:
                self._fire_bullet()
            elif event.key == pygame.K_q:
                self._write_high_score()
                sys.exit()
            elif event.key == pygame.K_p and not self.game_active:
                self._start_game()
            elif event.key == pygame.K_UP:
                self.ship.moving_up = True
            elif event.key == pygame.K_DOWN:
                self.ship.moving_down = True 

     
    def _check_keyup_events(self,event):
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = False  
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = False 
            elif event.key == pygame.K_UP:
                self.ship.moving_up = False
            elif event.key == pygame.K_DOWN:
                self.ship.moving_down =False

    
    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    
    def _update_bullets_(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)
        self._check_bulet_alien_collisions()

    
    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.sb.show_score()


        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()
    
    
    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()   #更新外星舰队中所有外星人的位置

        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()    
    
    
    def _create_alien(self,x_position,y_position):
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.y = y_position
        new_alien.rect.x = x_position
        self.aliens.add(new_alien)

    
    def _create_fleet(self):
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        current_x = alien_width
        current_y = alien_height
        
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width -2 * alien_width):
                self._create_alien(current_x,current_y)
                current_x += 2 * alien_width
            
            current_x = alien_width
            current_y += 2 *alien_height


    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edge():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.alien_drop_speed
        self.settings.fleet_direction *= -1


    def _check_bulet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(
            self.bullets,self.aliens,True,True    #子弹飞击中敌人后，子弹和敌人都消失。False 1
        )  

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            self.stats.level += 1
            self.sb.prep_level() 


    def _ship_hit(self):
        if self.stats.ship_left > 0:
            self.stats.ship_left -= 1 
            self.sb.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.game_active = False
            self._write_high_score()
            pygame.mouse.set_visible(True)    


    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break


    def _write_high_score(self):
        path = Path("score.txt")
        path.write_text(str(self.stats.high_score))                                



            




    
    
                                 

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()                    
