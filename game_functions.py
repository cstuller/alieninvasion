import sys
from time import sleep
import pygame
from bullet import Bullet
from alien import Alien

def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    '''respond to keypresses and mouse events.'''
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats, sb, play_button, ship, aliens, bullets)

        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)


def check_keydown_events(event, ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    '''respond to keypresses'''
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True

    elif event.key == pygame.K_LEFT:
        ship.moving_left = True

    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)

    elif event.key == pygame.K_q:
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    elif event.key == pygame.K_r:
        stats.game_active = False
        pygame.mouse.set_visible(True)        

    elif event.key == pygame.K_p and not stats.game_active:
        start_game(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets)

def check_keyup_events(event, ship):
    '''respond to key releases'''
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False

    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y):
    '''start a new game when the player clicks Play'''
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_game(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets)

def start_game(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    '''start the game over'''
    #reset to level 1
    ai_settings.initialize_dynamic_settings()
    
    #hide the mouse cursor
    pygame.mouse.set_visible(False)
        
    #reset the game statistics
    stats.reset_stats()
    stats.game_active = True

    #reset the scoreboard images
    sb.prep_score()
    sb.prep_high_score()
    sb.prep_level()
    sb.prep_ships()

    #empty the list of aliens and bullets
    aliens.empty()
    bullets.empty()

    #create a new fleet and center the ship
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()

def get_number_rows(ai_settings, ship_height, alien_height):
    '''determine the number of rows of aliens that fit on the screen'''
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows

def get_number_aliens_x(ai_settings, alien_width):
    '''determine the number of aliens that fit in a row'''
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    '''create an alien and place it in the row'''
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)    

def create_fleet(ai_settings, screen, ship, aliens):
    '''create a full fleet of aliens'''
    #create an alien and find the number of aliens in a row
    #spacing between each alien is equal to one alien width
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)

    #create the first row of aliens
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)

def check_fleet_edges(ai_settings, aliens):
    '''respond appripriately if any aliens have reached an edge'''
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    '''drop the entire fleet and change the fleet's direction'''
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def fire_bullet(ai_settings, screen, ship, bullets):
    '''fire a bullet if the limit has not been reached yet'''
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets):
    '''respond to ship being hit by alien'''
    if stats.ships_left > 0:
        #decrement ships left
        stats.ships_left -= 1

        #update scoreboard
        sb.prep_ships()

        #empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        #create a new fleet and center the ship
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        #pause
        sleep(0.5)

    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

def check_high_score(stats, sb):
    '''check to see if there's a new high score'''
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()

def check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets):
    '''check if any aliens have reached the bottom of the screen'''
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            #treat this the same as if the ship got hit
            ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
            break

def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    '''respond to bullet-alien collisions'''
    #remove any bullets and aliens that have collided
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)

    #if the fleet is defeated, destroy all bullets, speed up game and build a new fleet
    if len(aliens) == 0:
        bullets.empty()
        ai_settings.increase_speed()

        #increase level
        stats.level += 1
        sb.prep_level()
        
        create_fleet(ai_settings, screen, ship, aliens)        

def update_screen(ai_settings, screen, stats, ship, sb, aliens, bullets, play_button):
    '''update images on the screen and flip to the new screen'''
    #redraw the screen during each pass through the loop
    screen.fill(ai_settings.bg_color)

    #redraw all bullets behind ship and aliens
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    #draw the score
    sb.show_score()
    
    #redraw the ship
    ship.blitme()
    aliens.draw(screen)

    #draw the play button if the game is inactive
    if stats.game_active == False:
        play_button.draw_button()

    #make the most recently drawn screen visible
    pygame.display.flip()

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    '''update position of bullets and get rid of old bullets'''
    bullets.update()
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    #check for any bullets that have hit aliens
    #if so, get rid of the bullet and the alien
    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)

def update_aliens(ai_settings, stats, screen, sb, ship, aliens, bullets):
    '''check if fleet is at an edge, then update all alien positions'''
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    #look for alien-ship collisions
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)
    #look for aliens hitting the bottom of the screen
    check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets)
