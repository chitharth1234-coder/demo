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
PURPLE = (200, 140, 255)
ORANGE = (255, 180, 100)

PLAYER_COLORS = [(0, 0, 255), (255, 0, 0)]

FONT = pygame.font.SysFont("arial", 11, True)
UI_FONT = pygame.font.SysFont("arial", 16, True)

TILE_SIZE = WIDTH // 10

# ---------------- BOARD ----------------
bottom = [
    ("GO","start"),("Library","place"),("Exam","exam"),("Lab","place"),
    ("Mid-Sem","exam"),("Sports","bonus"),("Cafeteria","place"),
    ("Activity","bonus"),("Auditorium","place"),("Jail","none")
]

right = [
    ("Discipline","none"),("Dept A","place"),("Lab 2","place"),
    ("Dept B","place"),("Surprise Test","exam"),("Dept C","place"),
    ("Conference","bonus"),("Dept D","place"),("Project Review","bonus")
]

top = [
    ("Free Pass","none"),("Admin","place"),("Exam","exam"),
    ("Placement","place"),("Finals","exam"),("Innovation","bonus"),
    ("Library 2","place"),("Activity","bonus"),("Cultural Hall","place")
]

left = [
    ("Parking","none"),("Hostel A","place"),("Workshop","bonus"),
    ("Hostel B","place"),("Quiz","exam"),("Research","bonus"),
    ("Seminar","bonus"),("Hostel C","place"),("Internship","bonus")
]

tiles = bottom + right + top + left
owners = [None]*len(tiles)

# ---------------- PLAYERS ----------------
players = [{"pos":0,"credits":150},{"pos":0,"credits":150}]
current_player = 0
dice_value = 0
waiting = False
message = "Press SPACE to roll"

events = [("Hackathon Win",20),("Late Submission",-15),
          ("Sports Victory",15),("Attendance Shortage",-10)]

# ---------------- DRAW BOARD ----------------
def draw_tile(x,y,name,color):
    pygame.draw.rect(screen,color,(x,y,TILE_SIZE,TILE_SIZE))
    pygame.draw.rect(screen,BLACK,(x,y,TILE_SIZE,TILE_SIZE),2)
    text = FONT.render(name,True,BLACK)
    screen.blit(text,(x+5,y+5))

def draw_board():
    screen.fill(WHITE)

    for i,t in enumerate(bottom):
        draw_tile(i*TILE_SIZE,HEIGHT-TILE_SIZE,t[0],RED)

    for i,t in enumerate(right):
        draw_tile(WIDTH-TILE_SIZE,HEIGHT-(i+2)*TILE_SIZE,t[0],ORANGE)

    for i,t in enumerate(top):
        draw_tile(WIDTH-(i+2)*TILE_SIZE,0,t[0],BLUE)

    for i,t in enumerate(left):
        draw_tile(0,(i+1)*TILE_SIZE,t[0],PURPLE)

# ---------------- POSITION ----------------
def get_pos(index):

    if index<10:
        return index*TILE_SIZE+TILE_SIZE//2, HEIGHT-TILE_SIZE//2

    elif index<19:
        i=index-10
        return WIDTH-TILE_SIZE//2, HEIGHT-(i+2)*TILE_SIZE+TILE_SIZE//2

    elif index<28:
        i=index-19
        return WIDTH-(i+2)*TILE_SIZE+TILE_SIZE//2, TILE_SIZE//2

    else:
        i=index-28
        return TILE_SIZE//2, (i+1)*TILE_SIZE+TILE_SIZE//2

# ---------------- TILE EFFECT ----------------
def apply(player,t_type,name):
    global message
    if t_type=="exam":
        loss=random.randint(10,25)
        player["credits"]-=loss
        message=f"Exam Stress -{loss}"

    elif t_type=="bonus":
        e,val=random.choice(events)
        player["credits"]+=val
        message=f"{e} {val:+}"

    elif t_type=="place":
        cost=30
        if owners[player["pos"]] is None and player["credits"]>=cost:
            owners[player["pos"]]=current_player
            player["credits"]-=cost
            message=f"Bought {name}"

    elif t_type=="start":
        player["credits"]+=10
        message="GO +10"

    else:
        message="Nothing happened"

# ---------------- GAME LOOP ----------------
clock=pygame.time.Clock()
run=True

while run:
    clock.tick(60)
    draw_board()

    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            run=False

        if e.type==pygame.KEYDOWN:

            if e.key==pygame.K_SPACE and not waiting:
                dice_value=random.randint(1,6)
                p=players[current_player]
                p["pos"]=(p["pos"]+dice_value)%len(tiles)
                name,typ=tiles[p["pos"]]
                message=f"Player {current_player+1} on {name} (A=Act S=Skip)"
                waiting=True

            elif waiting:
                name,typ=tiles[players[current_player]["pos"]]
                if e.key==pygame.K_a:
                    apply(players[current_player],typ,name)
                    waiting=False
                    current_player=(current_player+1)%2
                if e.key==pygame.K_s:
                    waiting=False
                    current_player=(current_player+1)%2

    for i,p in enumerate(players):
        x,y=get_pos(p["pos"])
        pygame.draw.circle(screen,PLAYER_COLORS[i],(x,y),10)

    screen.blit(UI_FONT.render(f"Turn: Player {current_player+1}",True,BLACK),(10,10))
    screen.blit(UI_FONT.render(f"Dice: {dice_value}",True,BLACK),(10,35))
    screen.blit(UI_FONT.render(f"P1:{players[0]['credits']}  P2:{players[1]['credits']}",True,BLACK),(10,60))
    screen.blit(UI_FONT.render(message,True,BLACK),(10,90))

    pygame.display.update()

pygame.quit()
sys.exit()