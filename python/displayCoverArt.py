import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
import requests
from io import BytesIO
from PIL import Image
import os
import configparser
from bs4 import BeautifulSoup
import urllib.request
import pygame

if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]

    # Configuration file    
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, '../config/options.ini')

    # Configures logger for storing song data    
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='spotipy.log',level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')

    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler('spotipy.log', maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)

    # Configuration
    config = configparser.ConfigParser()
    config.read(filename)

    prevSong = ""
    currentSong = ""
    try:
        while True:
            try:
                songInfo = getSongInfo(username, token_path)
                imageURL, songName, artistName = songInfo[1], songInfo[0], songInfo[2]
                currentSong = imageURL

                if prevSong != currentSong:
                    album_cover_path = os.path.join(dir, 'client/album_cover.png')
                    urllib.request.urlretrieve(imageURL, album_cover_path)

                    response = requests.get(imageURL)
                    image = Image.open(BytesIO(response.content))
                    image.thumbnail((250, 250), Image.Resampling.LANCZOS)
                    prevSong = currentSong

                    htmlFilePath = os.path.join(dir, 'client/spotipi.html')

                    # Edit html file
                    with open(htmlFilePath) as html_file:
                        soup = BeautifulSoup(html_file.read(), features='html.parser')
                        soup.h1.string.replace_with(songName)
                        soup.h2.string.replace_with(artistName)
                        soup.find('img', id='album-cover')['src'] = album_cover_path
                        new_text = soup.prettify()
                    
                    with open(htmlFilePath, mode='w') as new_html_file:
                        new_html_file.write(new_text)
                    
                    logger.info(f"Updated display: {songName} by {artistName}")
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)

else:
    print("Usage: %s username token_path" % (sys.argv[0],))
    sys.exit()

def initialize_display():
    pygame.init()
    return pygame.display.set_mode((800, 480), pygame.FULLSCREEN)  # Adjust resolution as needed

def fade_transition(screen, old_surface, new_surface, fade_speed=5):
    fade_alpha = 0
    clock = pygame.time.Clock()
    
    while fade_alpha < 255:
        fade_alpha += fade_speed
        if fade_alpha > 255:
            fade_alpha = 255
        
        screen.blit(old_surface, (0, 0))
        new_surface.set_alpha(fade_alpha)
        screen.blit(new_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

def update_display(screen, image_path, song_name, artist_name):
    new_surface = pygame.Surface(screen.get_size())
    new_surface.fill((255, 255, 255))  # White background
    
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (300, 300))  # Adjust size as needed
    new_surface.blit(image, (50, 90))
    
    font = pygame.font.Font(None, 36)
    song_text = font.render(song_name, True, (0, 0, 0))
    artist_text = font.render(artist_name, True, (0, 0, 0))
    new_surface.blit(song_text, (400, 150))
    new_surface.blit(artist_text, (400, 200))
    
    old_surface = screen.copy()
    fade_transition(screen, old_surface, new_surface)

def main():
    screen = initialize_display()
    prev_image_url = None
    try:
        while True:
            try:
                songInfo = getSongInfo(username, token_path)
                imageURL, songName, artistName = songInfo[1], songInfo[0], songInfo[2]
                
                if imageURL and imageURL != prev_image_url:  # Only update if there's a new song playing
                    album_cover_path = os.path.join(dir, 'album_cover.png')
                    urllib.request.urlretrieve(imageURL, album_cover_path)
                    update_display(screen, album_cover_path, songName, artistName)
                    logger.info(f"Updated display: {songName} by {artistName}")
                    prev_image_url = imageURL
                
                # Add a delay of 10 seconds between checks
                time.sleep(10)
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(10)  # Also add a delay here in case of errors
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()
