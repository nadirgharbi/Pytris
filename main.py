from settings import *
from tetris import Tetris, Text
import sys
import pathlib

class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption('Tetris')
        icon = pg.image.load(TETRIS_ICON)
        pg.display.set_icon(icon)
        self.screen = pg.display.set_mode(WIN_RES)
        self.clock = pg.time.Clock()
        self.set_timer()
        self.images = self.load_images()
        self.tetris = Tetris(self)
        self.text = Text(self)

        self.music_enabled = True
        self.speaker_on = pg.image.load(SPEAKER_ON_IMG)
        self.speaker_on = pg.transform.scale(self.speaker_on, (50, 50))
        self.speaker_off = pg.image.load(SPEAKER_OFF_IMG)
        self.speaker_off = pg.transform.scale(self.speaker_off, (50, 50))

 
    def load_images(self):
        files = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        images = [pg.image.load(file).convert_alpha() for file in files]
        images = [pg.transform.scale(image, (TILE_SIZE, TILE_SIZE)) for image in images]
        return images

    def set_timer(self):
        self.user_event = pg.USEREVENT + 0
        self.fast_user_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        self.tetris.update()
        self.clock.tick(FPS)

    def draw(self):
        self.screen.fill(color=BG_COLOR)
        self.screen.fill(color=FIELD_COLOR, rect=(0, 0, *FIELD_RES))
        self.tetris.draw()
        self.text.draw()

        # icône
        icon = self.speaker_on if self.music_enabled else self.speaker_off
        self.speaker_rect = self.get_speaker_rect()
        self.screen.blit(icon, self.speaker_rect.topleft)

        # texte centré sous l’icône
        label = f"Musique : {'Activé' if self.music_enabled else 'Désactivé'}"
        font_size = int(TILE_SIZE * 0.5)
        text_rect = self.text.font.get_rect(label, size=font_size)
        text_pos = (self.speaker_rect.centerx - text_rect.width / 2,
                    self.speaker_rect.bottom + 8)
        self.text.font.render_to(self.screen, text_pos, label, fgcolor='white', size=font_size)

        pg.display.flip()

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            if not pg.mixer.get_init():
                pg.mixer.init()
            if not pg.mixer.music.get_busy():
                pg.mixer.music.load(BGM_SRC)
                pg.mixer.music.play(-1)
        else:
            pg.mixer.music.stop()

    def get_speaker_rect(self):
        icon = self.speaker_on if self.music_enabled else self.speaker_off
        # centre du panneau de droite
        panel_center_x = FIELD_RES[0] + (WIN_W - FIELD_RES[0]) / 2
        # place l’icône vers le bas (ajuste 0.78 si tu veux)
        icon_rect = icon.get_rect(center=(panel_center_x, WIN_H * 0.78))
        return icon_rect

    def check_events(self):
        self.anim_trigger = False
        self.fast_anim_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                self.tetris.control(pressed_key=event.key)
            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.fast_user_event:
                self.fast_anim_trigger = True

            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  
                icon_rect = getattr(self, "speaker_rect", self.get_speaker_rect())
                if icon_rect.collidepoint(mouse_pos):
                    self.toggle_music()

    def run(self):
        if self.music_enabled and not pg.mixer.music.get_busy():
            pg.mixer.music.load(BGM_SRC)
            pg.mixer.music.play(-1)
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    app = App()
    app.run()