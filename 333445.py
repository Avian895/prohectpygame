import pygame
import pygame_gui
import sys
import math
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("игра")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
PLAYER_COLOR = BLACK
pygame.init()
FONT = pygame.font.SysFont("Arial", 30)
# Сложности
DIFFICULTIES = ["Практика", "Легко", "Нормально", "Хардкор"]
# Игровые объекты
player_speed = 5
player = pygame.Rect(300, 300, 50, 50)  # Черный кружок (персонаж)
player_pos = [WIDTH // 2, HEIGHT // 2]
player_size = 20
# Режим света
light_mode = "circle"  # "circle" или "flashlight"
# Стены (кортежи с координатами)
walls = [
    ((100, 100), (700, 100)),
    ((700, 100), (700, 500)),
    ((700, 500), (100, 500)),
    ((100, 500), (100, 100)),
]
# Проверка столкновений с стенами
def check_collision(rect, walls):
    for wall_start, wall_end in walls:
        x1, y1 = wall_start
        x2, y2 = wall_end
        if rect.clipline(x1, y1, x2, y2):
            return True
    return False
def draw_light(mouse_pos):  # все фигня - миша переделывай
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 255))  # Полупрозрачный черный фон -> не работатет
    if light_mode == "circle":
        # Градиентный круг света вокруг игрока(чет не так)
        for radius in range(250, 0, -5):
            alpha = int(255 * (radius / 250))  # Плавное уменьшение яркости
            pygame.draw.circle(overlay, (0, 0, 0, alpha), player_pos, radius)
    elif light_mode == "flashlight":
        # Вектор направления от игрока к мыши
        dx, dy = mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1]
        angle = math.atan2(dy, dx)
        # #todo Создание треугольника света -> не работает
        flashlight_length = 300
        flashlight_width = 100
        for i in range(20, 0, -1):
            alpha = int(255 * (i / 20))  # todo Плавное уменьшение яркости - > не работает
            length = flashlight_length * (i / 20)
            width = flashlight_width * (i / 20)
            left_point = (
                player_pos[0] + length * math.cos(angle - 0.2),
                player_pos[1] + length * math.sin(angle - 0.2),
            )
            right_point = (
                player_pos[0] + length * math.cos(angle + 0.2),
                player_pos[1] + length * math.sin(angle + 0.2),
            )
            pygame.draw.polygon(
                overlay, (0, 0, 0, alpha), [player_pos, left_point, right_point]
            )
    screen.blit(overlay, (0, 0))
# Игровое окно
def game():
    global player
    pygame.display.set_caption("Игра")
    game_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    # Настройка предметов
    """тут долдны быть id предмета, для того что бы нельзя было кактусом открыть сейф"""
    items = [
        {
            "id": "key",
            "image": pygame.image.load("images/Unknown.jpeg"),  # Путь к изображению ключа
            "rect": pygame.Rect(200, 200, 40, 40),  # Размер и позиция ключа
        }
    ]
    for item in items:
        item["image"] = pygame.transform.scale(item["image"], (item["rect"].width, item["rect"].height))
    held_item = None  # Текущий предмет в руках игрока
    # Параметры стены и двери
    wall_thickness = 10
    door_width = 100  # Увеличенное отверстие для двери
    door = {
        "rect": pygame.Rect(350, 100, door_width, wall_thickness),  # Размер и позиция двери
        "is_open": False,  # Состояние двери (закрыта/открыта)
    }
    # Стены с учетом выреза под дверь
    walls = [
        ((100, 100), (350, 100)),  # Левая часть верхней стены
        ((450, 100), (700, 100)),  # Правая часть верхней стены
        ((700, 100), (700, 500)),  # Правая стена
        ((700, 500), (100, 500)),  # Нижняя стена
        ((100, 500), (100, 100)),  # Левая стена
    ]
    # Устанавливаем игрока внутри комнаты
    player.topleft = (150, 150)
    # Смещение камеры
    camera_offset = [0, 0]
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Обработка клавиш
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Подобрать предмет
                    for item in items:
                        if player.colliderect(item["rect"]) and held_item is None:
                            held_item = item
                            items.remove(item)  # Убираем предмет с карты
                            break
                if event.key == pygame.K_o:  # Положить предмет
                    if held_item:
                        held_item["rect"].center = player.center
                        items.append(held_item)  # Возвращаем предмет на карту
                        held_item = None
                if event.key == pygame.K_u:  # Использовать предмет
                    if (held_item and held_item["id"] == "key" and player.colliderect(door["rect"].inflate(10, 10))):
                        door["is_open"] = True
                        held_item = None  # Убираем ключ из рук
        # Управление движением персонажа
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1
        # Уменьшение скорости при движении по диагонали(я не до конца понимаю как оно работает)
        if dx != 0 and dy != 0:
            dx /= 2
            dy /= 2
        # Перемещение персонажа по оси X
        player.move_ip(dx * player_speed, 0)
        if check_collision(player, walls) or (not door["is_open"] and player.colliderect(door["rect"])):
            player.move_ip(-dx * player_speed, 0)  # Откат движения по X
        # Перемещение персонажа по оси Y
        player.move_ip(0, dy * player_speed)
        if check_collision(player, walls) or (not door["is_open"] and player.colliderect(door["rect"])):
            player.move_ip(0, -dy * player_speed)  # Откат движения по Y
        # Если предмет следует за игроком
        if held_item:
            held_item["rect"].center = (player.centerx + 10, player.centery + 10)
        # Обновление камеры
        camera_offset[0] = player.centerx - WIDTH // 2
        camera_offset[1] = player.centery - HEIGHT // 2
        # Отрисовка игрового поля
        game_screen.fill(BROWN)  # Пол - коричневый
        # Отрисовка стен
        for wall_start, wall_end in walls:
            wall_start_shifted = (wall_start[0] - camera_offset[0], wall_start[1] - camera_offset[1])
            wall_end_shifted = (wall_end[0] - camera_offset[0], wall_end[1] - camera_offset[1])
            pygame.draw.line(game_screen, RED, wall_start_shifted, wall_end_shifted, wall_thickness)
        # Отрисовка двери(почти как двери)
        door_shifted = door["rect"].move(-camera_offset[0], -camera_offset[1])
        if not door["is_open"]:
            pygame.draw.rect(game_screen, (128, 0, 128), door_shifted)  # Фиолетовая дверь
        # Отрисовка предметов
        for item in items:
            item_rect_shifted = item["rect"].move(-camera_offset[0], -camera_offset[1])
            game_screen.blit(item["image"], item_rect_shifted)
        # Отрисовка персонажа
        player_shifted = player.move(-camera_offset[0], -camera_offset[1])
        pygame.draw.circle(game_screen, PLAYER_COLOR, player_shifted.center, player.width // 2)
        # Получение позиции мыши
        mouse_pos = pygame.mouse.get_pos()
        # Рисуем света
        # todo ОНО РАБОТАЕТ КРИВО - ДОЛЖНО БЫТЬ ПЛАВНОЕ ЗАТЕМНЕНИЕ К КРАЯМ ЭКРАНА
        draw_light(mouse_pos)
        # Отрисовка предмета в руках
        if held_item:
            held_item_shifted = held_item["rect"].move(-camera_offset[0], -camera_offset[1])
            game_screen.blit(held_item["image"], held_item_shifted)
        pygame.display.flip()
        clock.tick(60)
class Menu:
    def __init__(self):
        self.selected_difficulty = DIFFICULTIES[0]
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        # Элементы интерфейса
        self.dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=DIFFICULTIES,
            starting_option=DIFFICULTIES[0],
            relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 4), (200, 30)),
            manager=self.manager
        )
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WIDTH // 2 - 100, HEIGHT // 2), (200, 40)),
            text="Начать игру",
            manager=self.manager
        )
    def draw(self, screen):
        screen.fill(BLACK)
        # Отображаем выбранную сложность
        difficulty_text = FONT.render(f"Сложность: {self.selected_difficulty}", True, WHITE)
        screen.blit(difficulty_text, (WIDTH // 2 - difficulty_text.get_width() // 2, HEIGHT // 4 - 50))
        # Обновляем интерфейс
        self.manager.update(pygame.time.get_ticks())
        self.manager.draw_ui(screen)
        pygame.display.flip()
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Обрабатываем события интерфейса
        self.manager.process_events(event)
        # Получаем выбранную сложность
        self.selected_difficulty = self.dropdown.selected_option
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_button:
                return "start_game"
        return None
# Главный цикл игры
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Меню игры")
    menu = Menu()
    while True:
        for event in pygame.event.get():
            action = menu.handle_event(event)
            if action == "start_game":
                # Закрытие меню и запуск игры
                return game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    light_mode = "flashlight" if light_mode == "circle" else "circle"
        menu.draw(screen)
if __name__ == "__main__":
    main()
