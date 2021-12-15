import re
import numpy as np

# content = json.load(codecs.open(jsonpath, 'r', 'utf-8-sig'))
# 感覺不需要轉移矩陣，應該x軸跟y軸分開算
matrix_left = np.array([[0.484,  -1.02],
                        [-0.0187, 0.096]])
matrix_right = np.array([[-0.571,  0.0154],
                        [0.00917, 0.0783]])


class coords:
    def __init__(self, side, x, y):
        self.side = side
        self.side_str = 'right' if self.side == 1 else 'left'
        self.x = x
        self.y = y
        self.matrix = matrix_right if self.side == 1 else matrix_left
        tr_x, tr_y = list(np.matmul(self.matrix, np.array([self.x, self.y])))
        self.tr_x = round(tr_x, 3)
        self.tr_y = round(tr_y, 3)

    def __str__(self):
        return f'{self.side_str} side fransformed from [{self.x}, {self.y}] to [{self.tr_x}, {self.tr_y}]'


def get_coords(txtpath: str):
    side = 1 if 'Right' in txtpath else 2
    regex = r"^\(X: (\d+), Y: (\d+)\)$"
    coords_list = []

    f = open(txtpath, 'r')
    line = f.readline()
    while line:
        # match regex to get x and y
        m = re.match(regex, line, re.DOTALL)
        if m:
            x_pos, y_pos = int(m.group(1)), int(m.group(2))
            coords_list.append(coords(side, x_pos, y_pos))
        else:
            pass

        line = f.readline()
        
    return coords_list


def generate_robot1_script(coords_list: list):
    script = ""
    for coord in coords_list:
        code_block = f"""SET V3={coord.side}
SET V1={coord.tr_x}
SET V2={coord.tr_y}

IF V3==1
// RIGHT
// START RIGHT MOVING
DELAY 1000
MOVE_JOINT P1 VEL=V10
MOVE_JOINT P2 VEL=V10
MOVE_POINT TX=V1 TY=-348 TZ=V2 VEL=V10

// SYNC WITH ROBOT2
SYNC 1
SYNC 2
DELAY 1500
MOVE_POINT P2 VEL=V10
SYNC 3
MOVE_POINT P7 VEL=V10
END

//------------------------------
IF V3==2
// LEFT
// START LEFT MOVING
DELAY 1000
MOVE_JOINT P9 VEL=V10
MOVE_JOINT P4 VEL=V10
MOVE_POINT TX=V1 TY=330 TZ=V2 VEL=V10

// SYNC WITH ROBOT2
SYNC 1
SYNC 2
DELAY 1500
MOVE_POINT P4 VEL=V10
SYNC 3
MOVE_POINT P8 VEL=V10

END

// ----- next one -----
"""

        script += code_block

    return script


def generate_robot2_script(coords_list: list):
    script = ""
    for coord in coords_list:
        code_block = f"""SET V3={coord.side}

IF V3==1
MOVE_JOINT P1 VEL=V10
MOVE_JOINT P2 VEL=V10
SYNC 1
MOVE_POINT A1=0 VEL=V10
DELAY 2000

//MOVE_POINT A1=70 VEL=V10
SYNC 2
MOVE_POINT P2 VEL=V10
SYNC 3

DELAY 2000
MOVE_POINT P7 VEL=V10

END

//-----------------------------------
IF V3==2
MOVE_JOINT P9 VEL=V10
MOVE_JOINT P4 VEL=V10

SYNC 1
MOVE_POINT A1=0 VEL=V10
DELAY 2000

//MOVE_POINT A1=70 VEL=V10
SYNC 2
MOVE_POINT P4 VEL=V10
SYNC 3
DELAY 2500
MOVE_POINT P8 VEL=V10

END

// ----- next one -----
"""

        script += code_block

    return script


def main():
    # get left & right coordinates
    coords_list = get_coords('Left_camera_location.txt')
    coords_list += get_coords('Right_camera_location.txt')

    for each in coords_list:
        print(each)

    # generate scripts for robots
    robot1_script = generate_robot1_script(coords_list)
    robot2_script = generate_robot2_script(coords_list)

    # save scripts
    dir_path = 'C:\\users\\PMC\\...'
    with open(f'{dir_path}\\robot1.script', 'w') as f:
        f.write(robot1_script)

    with open(f'{dir_path}\\robot2.script', 'w') as f:
        f.write(robot2_script)


if __name__ == '__main__':
    main()
