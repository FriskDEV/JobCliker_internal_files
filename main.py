import sys
import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

SIZE = (600, 600)
FPS = 30

fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("JobCliker")

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
GRAY = pygame.Color(50, 50, 50)
BUTTON_BG_COLOR = pygame.Color(68, 93, 255)
BUTTON_BORDER_COLOR = pygame.Color(85, 50, 232)
HOVER_COLOR = pygame.Color(100, 120, 255)
SPECIAL_COLOR = pygame.Color(255, 200, 0)
SPECIAL_HOVER_COLOR = pygame.Color(255, 230, 50)

FONT = pygame.font.SysFont("sysfont", 24)
FONT_BIG = pygame.font.SysFont("sysfont", 48)
FONT_SMALL = pygame.font.SysFont("sysfont", 18)

COOKIE_IMAGE = pygame.image.load("cookie.png")

try:
    BG_IMAGE = pygame.image.load("menu_bg.png")
    BG_IMAGE = pygame.transform.scale(BG_IMAGE, SIZE)
except FileNotFoundError:
    BG_IMAGE = None

try:
    TITLE_IMAGE = pygame.image.load("title.png")
    original_w, original_h = TITLE_IMAGE.get_size()
    ratio = min(400 / original_w, 500 / original_h)
    TITLE_IMAGE = pygame.transform.scale(TITLE_IMAGE, (int(original_w * ratio), int(original_h * ratio)))
except FileNotFoundError:
    TITLE_IMAGE = None

try:
    INTRO_IMAGE = pygame.image.load("intro.png")
    INTRO_IMAGE = pygame.transform.scale(INTRO_IMAGE, SIZE)
except FileNotFoundError:
    INTRO_IMAGE = None

try:
    FINAL_IMAGE = pygame.image.load("final.png")
    FINAL_IMAGE = pygame.transform.scale(FINAL_IMAGE, SIZE)
except FileNotFoundError:
    FINAL_IMAGE = None

try:
    SPECIAL_IMAGE = pygame.image.load("fin.png")
    SPECIAL_IMAGE = pygame.transform.scale(SPECIAL_IMAGE, (200, 100))
except FileNotFoundError:
    SPECIAL_IMAGE = None

COOKIES = 0
CPS = 0.0
SCENE = "menu"
SPECIAL_REQUIRED = 100000
CURRENT_MUSIC = None

SPECIAL_RECT = Rect(200, 450, 200, 100)


def play_music(filename):
    global CURRENT_MUSIC
    if CURRENT_MUSIC == filename:
        return
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1)
        CURRENT_MUSIC = filename
    except:
        pass


def reset_game():
    global COOKIES, CPS
    COOKIES = 0
    CPS = 0.0
    for item in items:
        item.count = 0


class MenuButton:
    def __init__(self, rect, text, color=None, hover=None):
        self.rect = rect
        self.text = text
        self.color = color or BUTTON_BG_COLOR
        self.hover = hover or HOVER_COLOR

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, 0, 8)
        pygame.draw.rect(surface, BUTTON_BORDER_COLOR, self.rect, 2, 8)
        text_surface = FONT.render(self.text, True, BLACK if self.color == SPECIAL_COLOR else WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def collidepoint(self, point):
        return self.rect.collidepoint(point)


class Item:
    def __init__(self, rect, text, base_price, base_cps_each, image_path=None):
        self.rect = rect
        self.text = text
        self.count = 0
        self.base_price = base_price
        self.cps_each = base_cps_each
        if image_path:
            try:
                img = pygame.image.load(image_path).convert_alpha()
                icon_size = int(self.rect.height * 0.8)
                self.image = pygame.transform.scale(img, (icon_size, icon_size))
            except FileNotFoundError:
                self.image = None
        else:
            self.image = None

    def draw(self, surface):
        pygame.draw.rect(surface, BUTTON_BG_COLOR, self.rect, 0)
        pygame.draw.rect(surface, BUTTON_BORDER_COLOR, self.rect, 2)
        x_offset = 10
        if self.image:
            icon_rect = self.image.get_rect()
            icon_rect.centery = self.rect.centery
            icon_rect.left = self.rect.left + 5
            surface.blit(self.image, icon_rect)
            x_offset = icon_rect.width + 10
        text_surface = FONT.render(
            str(self.count) + "x " + self.text + "  $" + str(int(self.price())),
            False, WHITE
        )
        text_rect = text_surface.get_rect()
        text_rect.topleft = (self.rect.left + x_offset, self.rect.top + self.rect.height * 0.25)
        surface.blit(text_surface, text_rect)

    def total_cps(self):
        return self.cps_each * self.count

    def price(self):
        return self.base_price * 1.15 ** self.count

    def click(self):
        global COOKIES
        price = self.price()
        if COOKIES >= price:
            self.count += 1
            COOKIES -= price
            calculate_cps()

    def collidepoint(self, point):
        return self.rect.collidepoint(point)


def make_items(text_list, base_price_list, cps_list, rect, spacing, image_paths=None):
    button_height = rect.height / len(text_list)
    button_width = rect.width
    buttons = []
    for i in range(len(text_list)):
        button_rect = Rect(
            rect.left,
            rect.top + i * (button_height + spacing),
            button_width,
            button_height
        )
        img_path = image_paths[i] if image_paths and i < len(image_paths) else None
        buttons.append(Item(button_rect, text_list[i], base_price_list[i], cps_list[i], img_path))
    return buttons


def calculate_cps():
    global CPS
    CPS = sum(item.total_cps() for item in items)

def update_cookies():
    global COOKIES
    COOKIES += CPS / FPS

def click_cookie():
    global COOKIES
    COOKIES += 1


cookie_rect = Rect(25, 250, COOKIE_IMAGE.get_width(), COOKIE_IMAGE.get_height())

items = make_items(
    ["Cursor", "Grandma", "Farm", "Mine", "Shipment"],
    [15, 100, 500, 10000, 40000],
    [0.1, 0.5, 4, 40, 100],
    Rect(350, 25, 250, 400), 5,
    image_paths=[
        "cursor.png",
        "grandma.png",
        "farm.png",
        "mine.png",
        "shipment.png"
    ]
)

menu_buttons = {
    "play":    MenuButton(Rect(200, 320, 200, 50), "Jugar"),
    "credits": MenuButton(Rect(200, 390, 200, 50), "Creditos"),
    "quit":    MenuButton(Rect(200, 460, 200, 50), "Salir"),
}

credits_button_back = MenuButton(Rect(200, 480, 200, 50), "Volver")

while True:
    screen.fill(BLACK)

    if SCENE == "menu":
        play_music("Menu.mp3")
        if BG_IMAGE:
            screen.blit(BG_IMAGE, (0, 0))
        else:
            screen.fill(GRAY)
        if TITLE_IMAGE:
            title_rect = TITLE_IMAGE.get_rect(center=(SIZE[0] // 2, 130))
            screen.blit(TITLE_IMAGE, title_rect)
        else:
            title = FONT_BIG.render("Cookie Clicker", True, WHITE)
            title_rect = title.get_rect(center=(SIZE[0] // 2, 100))
            screen.blit(title, title_rect)
        for button in menu_buttons.values():
            button.draw(screen)

    elif SCENE == "intro":
        play_music("Menu.mp3")
        if INTRO_IMAGE:
            screen.blit(INTRO_IMAGE, (0, 0))
        else:
            screen.fill(GRAY)
            t = FONT_BIG.render("Haz clic para jugar", True, WHITE)
            screen.blit(t, t.get_rect(center=(SIZE[0] // 2, SIZE[1] // 2)))

    elif SCENE == "game":
        play_music("Hora_de_Clikiar.mp3")
        screen.blit(COOKIE_IMAGE, cookie_rect)
        text_surface = FONT.render(
            str(int(COOKIES)) + "  +" + str(round(CPS, 1)) + " CPS",
            False, WHITE
        )
        text_rect = text_surface.get_rect()
        text_rect.topright = (SIZE[0] - 10, 10)
        screen.blit(text_surface, text_rect)
        for item in items:
            item.draw(screen)
        if COOKIES >= SPECIAL_REQUIRED:
            if SPECIAL_IMAGE:
                screen.blit(SPECIAL_IMAGE, SPECIAL_RECT)
            else:
                fallback = MenuButton(SPECIAL_RECT, "Entregar trabajo", SPECIAL_COLOR, SPECIAL_HOVER_COLOR)
                fallback.draw(screen)
        update_cookies()

    elif SCENE == "final":
        play_music("Menu.mp3")
        if FINAL_IMAGE:
            screen.blit(FINAL_IMAGE, (0, 0))
        else:
            screen.fill(GRAY)
            t = FONT_BIG.render("FIN", True, WHITE)
            t2 = FONT.render("Haz clic para volver a jugar", True, WHITE)
            screen.blit(t, t.get_rect(center=(SIZE[0] // 2, SIZE[1] // 2 - 40)))
            screen.blit(t2, t2.get_rect(center=(SIZE[0] // 2, SIZE[1] // 2 + 40)))

    elif SCENE == "credits":
        play_music("Menu.mp3")
        if BG_IMAGE:
            screen.blit(BG_IMAGE, (0, 0))
        else:
            screen.fill(GRAY)
        t1 = FONT_BIG.render("Creditos", True, WHITE)
        t2 = FONT.render("Juego creado con Pygame", True, WHITE)
        t3 = FONT.render("Canal: FriskDEV", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SIZE[0] // 2, 150)))
        screen.blit(t2, t2.get_rect(center=(SIZE[0] // 2, 280)))
        screen.blit(t3, t3.get_rect(center=(SIZE[0] // 2, 340)))
        credits_button_back.draw(screen)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if SCENE == "menu":
                if menu_buttons["play"].collidepoint(event.pos):
                    SCENE = "intro"
                elif menu_buttons["credits"].collidepoint(event.pos):
                    SCENE = "credits"
                elif menu_buttons["quit"].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            elif SCENE == "intro":
                SCENE = "game"
            elif SCENE == "game":
                if COOKIES >= SPECIAL_REQUIRED and SPECIAL_RECT.collidepoint(event.pos):
                    SCENE = "final"
                else:
                    for item in items:
                        if item.collidepoint(event.pos):
                            item.click()
                            break
                    if cookie_rect.collidepoint(event.pos):
                        click_cookie()
            elif SCENE == "final":
                reset_game()
                SCENE = "menu"
            elif SCENE == "credits":
                if credits_button_back.collidepoint(event.pos):
                    SCENE = "menu"

    pygame.display.update()
    fpsClock.tick(FPS)