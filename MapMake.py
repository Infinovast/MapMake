import random
import os
import time
from colorama import init, Fore, Style
from enum import Enum, auto
import opensimplex as noise  # 用于生成 Simplex Noise

init()  # 初始化 colorama

# 地图块类型枚举
class TileType(Enum):
    LAND = auto()  # 陆地
    FOREST = auto()  # 森林
    RIVER = auto()  # 河流
    WATER = auto()  # 水域

# 地图块对应的颜色
TILE_COLORS = {
    TileType.LAND: Fore.YELLOW + Style.BRIGHT,
    TileType.FOREST: Fore.GREEN + Style.BRIGHT,
    TileType.RIVER: Fore.BLUE + Style.BRIGHT,
    TileType.WATER: Fore.BLUE + Style.BRIGHT,
}

# 地图块对应的字符
TILE_CHARS = {
    TileType.LAND: "L",
    TileType.FOREST: "F",
    TileType.RIVER: "R",
    TileType.WATER: "W",
}

# 地图大小
map_size = 41

water_max = 0.0
land_max = 0.0
forest_max = 0.0

def generate_simplex_noise_map(seed, scale=20.0):
    """使用 Simplex Noise 生成地图数据"""
    random.seed(seed)
    noise_seed = random.randint(0, 1000)  # Simplex Noise 需要一个整数种子
    noise.seed(noise_seed)  # 设置 Simplex Noise 的种子
    map_data = [[TileType.LAND for _ in range(map_size)] for _ in range(map_size)]

    # 生成地形（湖泊、森林、陆地）
    global water_max, land_max, forest_max
    water_max = random.randint(-4, -2) / 10
    land_max = random.randint(1, 3) / 10
    forest_max = random.randint(4, 6) / 10

    for y in range(map_size):
        for x in range(map_size):
            # 生成 Simplex Noise 值
            value = noise.noise2(x / scale, y / scale)

            # 根据噪声值确定地图块类型
            if value < water_max:
                map_data[y][x] = TileType.WATER  # 水域
            elif value < land_max:
                map_data[y][x] = TileType.LAND  # 陆地
            elif value < forest_max:
                map_data[y][x] = TileType.FOREST  # 森林
            else:
                map_data[y][x] = TileType.RIVER  # 河流

    # 生成河流
    generate_river(map_data)

    return map_data

def generate_river(map_data):
    """生成自然弯曲的河流"""
    # 随机选择一个起点（地图的边缘）
    start_side = random.randint(1, 4)  # 1: 上边, 2: 下边, 3: 左边, 4: 右边
    if start_side == 1:
        x, y = random.randint(0, map_size - 1), 0  # 上边
        main_direction = (0, 1)  # 主要方向：向下
    elif start_side == 2:
        x, y = random.randint(0, map_size - 1), map_size - 1  # 下边
        main_direction = (0, -1)  # 主要方向：向上
    elif start_side == 3:
        x, y = 0, random.randint(0, map_size - 1)  # 左边
        main_direction = (1, 0)  # 主要方向：向右
    else:
        x, y = map_size - 1, random.randint(0, map_size - 1)  # 右边
        main_direction = (-1, 0)  # 主要方向：向左

    # 河流生成方向（主要方向 + 随机偏移）
    # directions = [
    #     main_direction,  # 主要方向
    #     (main_direction[0], main_direction[1]),  # 主要方向（重复以增加权重）
    #     (main_direction[1], main_direction[0]),  # 斜向方向 1
    #     (-main_direction[1], -main_direction[0]),  # 斜向方向 2
    # ]
    directions = ([
        main_direction for _ in range(3)]  # 主要方向
    +[
        (main_direction[1], main_direction[0]),  # 斜向方向 1
        (-main_direction[1], -main_direction[0]),  # 斜向方向 2
        (1, main_direction[1]) if start_side <= 2 else (main_direction[1], 1),  # 斜向方向 3
        (-1, main_direction[1]) if start_side <= 2 else (main_direction[1], -1)  # 斜向方向 4
    ])

    # 生成河流直到超出边界
    while 0 <= x < map_size and 0 <= y < map_size:
        # 设置当前点为河流
        if map_data[y][x] != TileType.WATER:  # 避免覆盖湖泊
            map_data[y][x] = TileType.RIVER

        # 随机选择下一个方向（倾向于主要方向）
        direction = random.choice(directions)
        dx, dy = direction
        x += dx
        y += dy

        # 检查是否靠近湖泊（确保 x 和 y 在范围内）
        try:
            if (
                (x > 0 and map_data[y][x - 1] == TileType.WATER) or
                (x < map_size - 1 and map_data[y][x + 1] == TileType.WATER) or
                (y > 0 and map_data[y - 1][x] == TileType.WATER) or
                (y < map_size - 1 and map_data[y + 1][x] == TileType.WATER)
            ):
                # break  # 河流连接到湖泊，停止生成
                generate_river(map_data)
                return
        except IndexError:
            break

def output(map_data, set_block):
    """输出地图"""
    for row in map_data:
        for tile in row:
            print(TILE_COLORS[tile], end="")  # 设置颜色
            if set_block:
                print("■", end="")  # 输出方块
            else:
                print(f"{TILE_CHARS[tile]:2}", end="")  # 输出字符
        print()  # 换行
    print(Style.RESET_ALL)  # 重置颜色

def main():
    seed = int(time.time())
    set_block = False
    map_data = generate_simplex_noise_map(seed)

    os.system("title Harold's GIS")  # 更改控制台标题
    print("Harold's GIS [版本 3.0]")
    print("Copyright(c) 2025 Harold. All rights reserved.\n")
    print("输入 '?' 查看帮助\n")

    while True:
        command = input("Command> ").strip().lower()
        if command == "?" or command == "？":
            print("\n帮助:")
            print("generate - 生成地图")
            print("print    - 打印地图")
            print("r        - 随机种子生成并打印地图(更便捷)")
            print("data     - 显示当前参数")
            print("block    - 切换方块显示模式")
            print("map      - 设置地图尺寸")
            print("seed     - 设置种子")
            print("quit     - 退出程序\n")
        elif command == "generate":
            map_data = generate_simplex_noise_map(seed)
            print("地图已生成！\n")
        elif command == "print":
            os.system("cls")  # 清屏
            output(map_data, set_block)  # 输出地图
        elif command == "data":
            global map_size
            print(f"地图尺寸: {map_size}\n种子: {seed}\n水、陆、森、河参数: {water_max, land_max, forest_max, 1}\n")
        elif command == "block":
            set_block = not set_block
            print(f"方块显示模式: {'开启' if set_block else '关闭'}\n")
        elif command == "map":
            try:
                # global map_size
                map_size = int(input(f"请输入新的地图尺寸({map_size}): "))
                map_data = generate_simplex_noise_map(seed)
                print("尺寸已设置，地图已重新生成！\n")
            except ValueError:
                print("错误: 尺寸必须是整数！\n")
        elif command == "seed":
            try:
                seed = int(input(f"请输入新种子({seed}): "))
                map_data = generate_simplex_noise_map(seed)
                print("种子已设置，地图已重新生成！\n")
            except ValueError:
                print("错误: 种子必须是整数！\n")
        elif command == "quit":
            print("退出程序。")
            break
        elif command == "r":
            seed = int(time.time())
            map_data = generate_simplex_noise_map(seed)
            os.system("cls")
            output(map_data, set_block)
        else:
            print("错误: 未知命令！输入 '?' 查看帮助。\n")

if __name__ == "__main__":
    main()