import fltk
from random import uniform, choice
import math
from time import time
import argparse
from playsound import playsound

val = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']

def parse_args():
    parser = argparse.ArgumentParser(description='Kollision')
    parser.add_argument('-m', '--mode', help='', type=str)
    return parser.parse_args()

WIDTH = 700
HEIGHT = 600

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, o):
        return Vector(self.x + o.x, self.y + o.y)

    def __iadd__(self, o):
        self.x += o.x
        self.y += o.y
        return self

    def __sub__(self, o):
        return Vector(self.x - o.x, self.y - o.y)

    def __isub__(self, o):
        self.x -= o.x
        self.y -= o.y
        return self

    def __mul__(self, o):
        return Vector(self.x * o.x, self.y * o.y)

    def __mul__(self, scal):
        return Vector(self.x * scal, self.y * scal)

    def __truediv__(self, o):
        return Vector(self.x / o.x, self.y / o.y)

    def __truediv__(self, scal):
        return Vector(self.x / scal, self.y / scal)

    def norm(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        norm = self.norm()
        return Vector(self.x / norm, self.y / norm)

    def dot(self, o):
        return self.x * o.x + self.y * o.y


class Ball():
    def __init__(self, color, x, y):
        self.pos = Vector(x, y)
        self.color = color
        self.radius = 24

    def update(self):
        pass

    def is_collision(self, o):
        return (o.pos - self.pos).norm() <= self.radius + o.radius

    def collide(self, o):
        pass

    def reset(self):
        pass

    def render(self):
        fltk.cercle(self.pos.x, self.pos.y, self.radius, self.color, self.color)


class Mob(Ball):
    def __init__(self):
        Ball.__init__(self, f'#{choice(val)}{choice(val)}{choice(val)}{choice(val)}{choice(val)}{choice(val)}', 0, 0)
        self.direction = (0, 0)
        self.ghost = time()

    def update(self):
        if time() - self.ghost > 3:
            self.ghost = 0
        if self.ghost:
            return
        self.pos += self.direction
        if self.pos.x < self.radius or self.pos.x > WIDTH - self.radius:
            self.direction.x *= -1
            if self.pos.x < self.radius:
                self.pos.x = self.radius
            else:
                self.pos.x = WIDTH - self.radius
        if self.pos.y < self.radius or self.pos.y > HEIGHT - self.radius:
            self.direction.y *= -1
            if self.pos.y < self.radius:
                self.pos.y = self.radius
            else:
                self.pos.y = HEIGHT - self.radius

    def collide(self, o):
        if self.ghost or o.ghost:
            return
        delta = (o.pos - self.pos)
        if delta.dot(o.direction - self.direction) > 0:
            return
        n = delta.normalize()
        v1 = self.direction.dot(n)
        v2 = o.direction.dot(n)
        self.direction += n * (v2-v1)
        o.direction += n * (v1-v2)

    def reset(self):
        self.pos = Vector(uniform(self.radius, WIDTH - self.radius), uniform(self.radius, HEIGHT - self.radius))
        self.direction = Vector(uniform(-2, 2), uniform(-2, 2)).normalize() * 6
        self.ghost = time()


class Player(Ball):
    def __init__(self):
        Ball.__init__(self, f'#{choice(val)}{choice(val)}{choice(val)}{choice(val)}{choice(val)}{choice(val)}', -WIDTH, -HEIGHT)
        self.collided = False

    class Collided(Exception):
        pass

    def update(self):
        self.pos.x = fltk.abscisse_souris()
        self.pos.y = fltk.ordonnee_souris()
        if self.pos.x < 0 + self.radius:
            self.pos.x = self.radius
        if self.pos.x > WIDTH - self.radius:
            self.pos.x = WIDTH - self.radius
        if self.pos.y < 0 + self.radius:
            self.pos.y = self.radius
        if self.pos.y > HEIGHT - self.radius:
            self.pos.y = HEIGHT - self.radius

    def collide(self, o):
        if not o.ghost:
            raise self.Collided()

    def reset(self):
        self.pos = Vector(-WIDTH, -HEIGHT)


class Kollision:
    def __init__(self, solid):
        fltk.cree_fenetre(WIDTH, HEIGHT, center="center")
        fltk.set_resizeable(False)
        self.state = 0
        self.balls = []
        self.balls.append(Player())
        self.start = 0
        self.duration = 0
        self.tick = 0
        self.pause_start = 0
        self.nb_mob = 4
        self.solid = solid
        for _ in range(self.nb_mob):
            self.balls.append(Mob())


    def __del__(self):
        fltk.ferme_fenetre()

    def reset_one(self, ball):
        ball.reset()
        for other in self.balls:
            if (ball != other):
                while ball.is_collision(other):
                    ball.reset()


    def ev_handling(self):

        def newgame(ev, tev):
            if tev == "ClicGauche":
                self.start = time()
                self.tick = int(time())
                self.state = 2
                fltk.set_cursor('none')
                self.balls = self.balls[0:self.nb_mob + 1]
                for ball in self.balls:
                    self.reset_one(ball)
            if tev == "Touche" and fltk.touche(ev) == "g":
                self.solid = False
            if tev == "Touche" and fltk.touche(ev) == "s":
                self.solid = True

        def paused(ev, tev):
            if tev == "ClicGauche" or (tev == "Touche" and fltk.touche(ev) == "space"):
                self.start += time() - self.pause_start
                self.state = 2
                fltk.set_cursor('none')
                self.tick = int(time())

        def ingame(ev, tev):
            if tev == "Touche" and fltk.touche(ev) == "space":
                self.state = 1
                self.pause_start = time()
                fltk.set_cursor('')

        handler = {
            0: newgame,
            1: paused,
            2: ingame,
            3: newgame
        }

        ev = fltk.donne_ev()
        tev = fltk.type_ev(ev)
        if tev == 'Quitte':
            return 1
        handler[self.state](ev, tev)
        return 0

    def collisions(self):
        nb_balls = len(self.balls)
        for i in range(nb_balls):
            current = self.balls[i]
            j = i + 1
            while j < nb_balls:
                other = self.balls[j]
                if current.is_collision(other) and (self.solid == True or i == 0):
                    current.collide(other)
                j += 1

    def render(self):

        def newgame():
            fltk.texte(WIDTH / 2, HEIGHT / 2, "Welcome to Kollision\nClick to start a game", "black", "center")

        def paused():
            fltk.texte(WIDTH / 2, HEIGHT / 2, " " * 14 + "Game paused\nClick or press space to resume", "black", "center")

        def endgame():
            fltk.texte(WIDTH / 2, HEIGHT / 2,\
            " " * 11 + f"GAME OVER\nYou survived for {self.duration} second,\n" + " " * 11 + "Click to restart"\
            , "black", "center")

        def death():
            self.duration = int(time() - self.start) - 3
            self.state = 3
            fltk.set_cursor('')
            playsound("assets/oof.wav")

        def ingame():
            date = int(time())
            if self.tick != date and (date - int(self.start)) % 20 == 0:
                self.balls.append(Mob())
                self.reset_one(self.balls[-1])
            try:
                self.collisions()
            except Player.Collided as e:
                death()
            for ball in self.balls:
                ball.update()
                ball.render()
            self.tick = date

        handler = {
            0: newgame,
            1: paused,
            2: ingame,
            3: endgame
        }
        handler[self.state]()

    def loop(self):
        while True:
            if self.ev_handling():
                break
            fltk.efface_tout()
            self.render()
            fltk.mise_a_jour()


def main(args):
    k = Kollision(args.mode != "gazeux")
    k.loop()

if __name__ == "__main__":
    main(parse_args())
