import random, datetime

SIZE = 100   # how many Prisoners
DAYS = 10   # How many days play the game
OPTION = 2

CLOSED = False
OPENED = True


class Room:
    def __init__(self, id, num):
        self.id = id
        self.num = num
        self.door = CLOSED

    def __repr__(self):
        return str(self.id) + ":" + str(self.num)


rooms = [Room(i, 0) for i in range(SIZE + 1)]


def print_rooms():
    print()
    for i in range(1, SIZE + 1):
        print('{0}:{1:02}{2} '.format(i, rooms[i].num, 'T' if rooms[i].door else 'F'), end=',')
        if i % 10 == 0:
            print()
    print()


def fill_random():
    nums = [i for i in range(1, SIZE+1)]
    random.shuffle(nums)
    for i in range(SIZE):
        rooms[i+1].num = nums[i]


def close_rooms():
    for r in rooms:
        r.door = CLOSED


def get_circle_of(x):
    num = rooms[x].num
    rooms_passed = [x]
    while num != x:
        rooms[num].door = CLOSED
        num = rooms[num].num
        rooms_passed.append(rooms[num].num)

    return rooms_passed


def open_rooms_option1():
    for P in range(1, SIZE+1):
        close_rooms()
        found = False

        for R in range(SIZE//2):
            d = random.randint(1, SIZE)
            if rooms[d].door == OPENED:
                while rooms[d].door == OPENED:
                    d = random.randint(1, SIZE)

            if rooms[d].num == P:
                found = True
                break
            else:
                rooms[d].door = CLOSED

        if not found:
            return False
    return True


def open_rooms_option2():
    for P in range(1, SIZE+1):
        close_rooms()
        if len(get_circle_of(random.randint(1,SIZE))) > SIZE//2:
            return False
    return True


def get_all_circles():
    circles = {}
    big_circle = []
    close_rooms()
    for i in range(1, SIZE + 1):
        if rooms[i].door == CLOSED:
            circle = get_circle_of(i)

            key = len(circle)
            circles[key] = circles.get(key, 0) + 1
            if len(circle) > SIZE//2:
                big_circle = circle
    close_rooms()
    return circles, big_circle


def split_circle(circle):
    rooms[circle[len(circle)-1]].num, rooms[circle[SIZE//2-1]].num = rooms[circle[SIZE//2-1]].num, rooms[circle[len(circle)-1]].num


def open_rooms_option3():
    circles, big_circle = get_all_circles()
    if big_circle != []:
        # print(f'\nBig Circle size  {len(big_circle)}')
        # print(f'start at {big_circle[0]} ')
        # print(f'path={big_circle}')
        split_circle(big_circle)

    return open_rooms_option2()


def main(option):
    cnt_success = 0
    print(f'\nPrisoners= {SIZE}. Days={DAYS}.')
    start = datetime.datetime.now()
    for i in range(DAYS):
        fill_random()
        if option == 1:
            if open_rooms_option1():
                cnt_success += 1
        elif option == 2:
            if open_rooms_option2():
                cnt_success += 1
        elif option == 3:
            if open_rooms_option3():
                cnt_success += 1

    delta_time = datetime.datetime.now() - start
    print(f'Amount of Success = {cnt_success} / {DAYS} days.')
    print(f'time={delta_time.total_seconds()} sec')


if __name__ == '__main__':
    main(OPTION)