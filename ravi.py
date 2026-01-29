import pygame
import sys
import random

pygame.init()

# ---------------- SCREEN ----------------
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("College Monopoly - Player Edition")

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (170, 230, 170)
RED = (255, 120, 120)
BLUE = (120, 170, 255)
YELLOW = (255, 255, 150)
ORANGE = (255, 180, 100)
PURPLE = (200, 140, 255)

PLAYER_COLORS = [(0, 0, 255), (255, 0, 0)]

FONT = pygame.font.SysFont("arial", 11, bold=True)
UI_FONT = pygame.font.SysFont("arial", 16, bold=True)

TILE_COUNT = 10
TILE_SIZE = WIDTH // TILE_COUNT
CENTER_SIZE = WIDTH - (TILE_SIZE * 2)

# ---------------- BOARD DATA ----------------
bottom = [
    ("GO", "start"), ("Library", "place"), ("Exam", "exam"), ("Lab", "place"),
    ("Mid-Sem", "exam"), ("Sports", "bonus"), ("Cafeteria", "place"),
    ("Activity", "bonus"), ("Auditorium", "place"), ("Jail", "none")
]

left = [
    ("Parking", "none"), ("Hostel A", "place"), ("Workshop", "bonus"),
    ("Hostel B", "place"), ("Quiz", "exam"), ("Research", "bonus"),
    ("Seminar", "bonus"), ("Hostel C", "place"), ("Internship", "bonus")
]

top = [
    ("Free Pass", "none"), ("Admin", "place"), ("Exam", "exam"),
    ("Placement", "place"), ("Finals", "exam"), ("Innovation", "bonus"),
    ("Library 2", "place"), ("Activity", "bonus"), ("Cultural Hall", "place")
]

right = [
    ("Discipline", "none"), ("Dept A", "place"), ("Lab 2", "place"),
    ("Dept B", "place"), ("Surprise Test", "exam"),
    ("Dept C", "place"), ("Conference", "bonus"),
    ("Dept D", "place"), ("Project Review", "bonus")
]

tiles = bottom + left + top + right
owners = [None] * len(tiles)

# ---------------- PLAYERS ----------------
players = [
    {"pos": 0, "credits": 150},
    {"pos": 0, "credits": 150}
]

current_player = 0
dice_value = 0
waiting_for_action = False
message = "Press SPACE to roll dice"

events = [
    ("Won Hackathon", 20),
    ("Late Submission", -15),
    ("Sports Victory", 15),
    ("Attendance Shortage", -10)
]

# ---------------- FUNCTIONS ----------------
def draw_tile(x, y, w, h, name, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    pygame.draw.rect(screen, BLACK, (x, y, w, h), 2)
    text = FONT.render(name, True, BLACK)
    screen.blit(text, (x + 5, y + 5))

def draw_board():
    screen.fill(WHITE)

    pygame.draw.rect(screen, GREEN, (TILE_SIZE, TILE_SIZE, CENTER_SIZE, CENTER_SIZE))
    pygame.draw.rect(screen, BLACK, (TILE_SIZE, TILE_SIZE, CENTER_SIZE, CENTER_SIZE), 3)

    title = UI_FONT.render("COLLEGE MONOPOLY", True, BLACK)
    screen.blit(title, (WIDTH // 2 - 90, HEIGHT // 2 - 10))

    for i, t in enumerate(bottom):
        draw_tile(i * TILE_SIZE, HEIGHT - TILE_SIZE, TILE_SIZE, TILE_SIZE, t[0], RED)

    for i, t in enumerate(left):
        draw_tile(0, HEIGHT - (i + 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE, t[0], PURPLE)

    for i, t in enumerate(top):
        draw_tile((i + 1) * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE, t[0], BLUE)

    for i, t in enumerate(right):
        draw_tile(WIDTH - TILE_SIZE, (i + 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE, t[0], ORANGE)

def get_tile_position(index):

    # Bottom row (0 - 9)
    if index < 10:
        x = index * TILE_SIZE + TILE_SIZE // 2
        y = HEIGHT - TILE_SIZE // 2
        return x, y

    # Left column (10 - 18)
    elif index < 19:
        i = index - 10
        x = TILE_SIZE // 2
        y = HEIGHT - (i + 2) * TILE_SIZE + TILE_SIZE // 2
        return x, y

    # Top row (19 - 27)
    elif index < 28:
        i = index - 19
        x = (i + 1) * TILE_SIZE + TILE_SIZE // 2
        y = TILE_SIZE // 2
        return x, y

    # Right column (28 - 36)
    else:
        i = index - 28
        x = WIDTH - TILE_SIZE // 2
        y = (i + 1) * TILE_SIZE + TILE_SIZE // 2
        return x, y


def apply_tile_effect(player, tile_type, tile_name):
    global message

    if tile_type == "exam":
        loss = random.randint(10, 25)
        player["credits"] -= loss
        message = f"Exam stress! -{loss} credits"

    elif tile_type == "bonus":
        event, val = random.choice(events)
        player["credits"] += val
        message = f"{event}! {val:+} credits"

    elif tile_type == "place":
        cost = random.randint(20, 40)
        if owners[player["pos"]] is None and player["credits"] >= cost:
            owners[player["pos"]] = current_player
            player["credits"] -= cost
            message = f"Bought {tile_name} for {cost} credits"
        else:
            message = "Cannot buy this place"

    elif tile_type == "start":
        player["credits"] += 10
        message = "Passed GO! +10 credits"

    else:
        message = "Nothing happened"

# ---------------- GAME LOOP ----------------
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    draw_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE and not waiting_for_action:
                dice_value = random.randint(1, 6)
                player = players[current_player]
                player["pos"] = (player["pos"] + dice_value) % len(tiles)
                tile_name, tile_type = tiles[player["pos"]]
                message = f"Player {current_player+1} landed on {tile_name}. A=Act S=Skip"
                waiting_for_action = True

            elif waiting_for_action:
                tile_name, tile_type = tiles[players[current_player]["pos"]]

                if event.key == pygame.K_a:
                    apply_tile_effect(players[current_player], tile_type, tile_name)
                    waiting_for_action = False
                    current_player = (current_player + 1) % len(players)

                elif event.key == pygame.K_s:
                    message = "Action skipped"
                    waiting_for_action = False
                    current_player = (current_player + 1) % len(players)

    for i, p in enumerate(players):
        px, py = get_tile_position(p["pos"])
        pygame.draw.circle(screen, PLAYER_COLORS[i], (px, py), 10)

    ui1 = UI_FONT.render(f"Player {current_player+1}'s Turn", True, BLACK)
    ui2 = UI_FONT.render(f"Dice: {dice_value}", True, BLACK)
    ui3 = UI_FONT.render(f"P1 Credits: {players[0]['credits']}  P2 Credits: {players[1]['credits']}", True, BLACK)
    ui4 = UI_FONT.render(message, True, BLACK)

    screen.blit(ui1, (10, 10))
    screen.blit(ui2, (10, 35))
    screen.blit(ui3, (10, 60))
    screen.blit(ui4, (10, 90))

    pygame.display.update()

pygame.quit()
sys.exit()