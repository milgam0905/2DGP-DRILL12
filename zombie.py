from pico2d import *

import random
import math

import common
import game_framework
import game_world
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector


# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

animation_names = ['Walk', 'Idle']


class Zombie:
    images = None

    def load_images(self):
        if Zombie.images == None:
            Zombie.images = {}
            for name in animation_names:
                Zombie.images[name] = [load_image("./zombie/" + name + " (%d)" % i + ".png") for i in range(1, 11)]
            Zombie.font = load_font('ENCR10B.TTF', 40)
            Zombie.marker_image = load_image('hand_arrow.png')


    def __init__(self, x=None, y=None):
        self.x = x if x else random.randint(100, 1180)
        self.y = y if y else random.randint(100, 924)
        self.load_images()
        self.dir = 0.0      # radian 값으로 방향을 표시
        self.speed = 0.0
        self.frame = random.randint(0, 9)
        self.state = 'Idle'
        self.ball_count = 0


        self.tx, self.ty = 1000, 1000
        # 여기를 채우시오.

        self.build_behavior_tree()

        self.patrol_locations = [(43, 274), (1118, 274), (1050, 494), (575, 804), (235, 991), (575, 804), (1050, 494), (1118, 274), (43, 274)]

        self.loc_no = 0


        self.rx = self.x + (self.x - common.boy.x)
        self.ry = self.y + (self.y - common.boy.y)

    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50


    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        # fill here
        self.bt.run() #매 프레임마다 행동트리를 root부터 시작해서 실행


    def draw(self):
        if math.cos(self.dir) < 0:
            Zombie.images[self.state][int(self.frame)].composite_draw(0, 'h', self.x, self.y, 100, 100)
        else:
            Zombie.images[self.state][int(self.frame)].draw(self.x, self.y, 100, 100)
        self.font.draw(self.x - 10, self.y + 60, f'{self.ball_count}', (0, 0, 255))
        Zombie.marker_image.draw(self.tx+25, self.ty-25)

        draw_circle(self.x, self.y, int(7.0 * PIXEL_PER_METER), 255, 255, 255, 255)




        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'zombie:ball':
            self.ball_count += 1


    def set_target_location(self, x=None, y=None):
        # 여기를 채우시오.
        if x is None or y is None:
            raise ValueError('목적위치가 설정되어애 합니다.')
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS



    def distance_less_than(self, x1, y1, x2, y2, r): #r은 미터단위
        # 여기를 채우시오.
        distance2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
        return distance2 < (PIXEL_PER_METER * r) ** 2



    def move_little_to(self, tx, ty):
        # 여기를 채우시오.
        distance = RUN_SPEED_PPS * game_framework.frame_time
        self.dir = math.atan2(ty - self.y, tx - self.x)
        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)



    def move_to(self, r=0.5):
        # 여기를 채우시오.
        self.state = 'Walk' #디버그 출력
        self.move_little_to(self.tx, self.ty)
        if self.distance_less_than(self.tx, self.ty, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING



    def set_random_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = random.randint(100, 1180), random.randint(100, 924)
        return BehaviorTree.SUCCESS


    def if_boy_nearby(self, distance):
        # 여기를 채우시오.
        if self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, distance):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL


    def move_to_boy(self, r=0.5):
        # 여기를 채우시오.
        self.move_little_to(common.boy.x, common.boy.y)
        if self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING



    def back_to_boy(self, r=7.0):
        self.move_little_to(self.rx, self.ry)
        if not self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING


    def get_patrol_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = self.patrol_locations[self.loc_no]
        self.loc_no = (self.loc_no + 1) % len(self.patrol_locations)
        return BehaviorTree.SUCCESS


    def build_behavior_tree(self):
        # 여기를 채우시오.
        #목표 지점을 설정하는 노드(1000, 1000)
        a1 = Action('Set target location', self.set_target_location, 500, 500)
        a2 = Action('Move to target', self.move_to, 0.5)

        a3 = Action('Set random location', self.set_random_location)

        c1 = Condition('소년이 근처에 있는가?', self.if_boy_nearby, 7)
        a4 = Action('소년한테 접근', self.move_to_boy)

        a5 = Action('순찰 위치 가져오기', self.get_patrol_location)

        a6 = Action('소년한테 도망', self.back_to_boy)

        move_to_target_sequence = Sequence('Move to target', a1, a2)

        wander = Sequence('Wander', a3, a2)

        chase_boy = Sequence('소년이 가까이 있으면 추적', c1, a4)

        chase_if_boy_near_or_wander = Selector('추적 또는 배회', chase_boy, wander)

        patrol = Sequence('순찰', a5, a2)

        patrol_or_chase = Selector('순찰 또는 추적', chase_boy, patrol)

        root = back_boy = Sequence('소년 가까이 있으면 도망', c1, a6)

        run_or_wander = Selector('도망 또는 배회', a6, wander)

        self.bt = BehaviorTree(root)

