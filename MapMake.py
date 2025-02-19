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

water_max = -0.3
land_max = 0.2
forest_max = 0.5

def generate_simplex_noise_map(seed, map_size, river_count, scale=20.0):
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
                map_data[y][x] = TileType.WATER  # 水域 -1 ~ waterMax
            elif value < land_max:
                map_data[y][x] = TileType.LAND  # 陆地 waterMax ~ landMax
            elif value < forest_max:
                map_data[y][x] = TileType.FOREST  # 森林 landMax ~ forestMax
            else:
                map_data[y][x] = TileType.RIVER  # 河流 forestMax ~ 1

    # 生成河流
    for _ in range(river_count):
        generate_river(map_data, map_size)

    return map_data

def generate_river(map_data, map_size):
    """生成自然弯曲的河流"""
    main_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    # 随机选择起点区域（地图内部或地图的边缘）
    start_side = random.randint(0, 4)  # 0: 内部, 1: 上边, 2: 下边, 3: 左边, 4: 右边

    if start_side == 0:  # 从地图中部的水域选择一个起点
        water_tiles = [(x, y) for y in range(map_size) for x in range(map_size) if map_data[y][x] == TileType.WATER or map_data[y][x] == TileType.RIVER]
        x, y = random.choice(water_tiles)
        main_direction = random.choice(main_directions)  # 随机选择一个主要方向
    elif start_side == 1:
        x, y = random.randint(0, map_size - 1), 0  # 上边
        main_direction = main_directions[0]  # 主要方向：向下
    elif start_side == 2:
        x, y = random.randint(0, map_size - 1), map_size - 1  # 下边
        main_direction = main_directions[1]  # 主要方向：向上
    elif start_side == 3:
        x, y = 0, random.randint(0, map_size - 1)  # 左边
        main_direction = main_directions[2]  # 主要方向：向右
    else:
        x, y = map_size - 1, random.randint(0, map_size - 1)  # 右边
        main_direction = main_directions[3]  # 主要方向：向左

    # 河流生成方向池（主要方向 + 随机偏移）
    directions = ([main_direction for _ in range(3)]  # 主要方向
                  + [(main_direction[1], main_direction[0]),  # 斜向方向 1
                     (-main_direction[1], -main_direction[0]),  # 斜向方向 2
                     (1, main_direction[1]) if start_side <= 2 else (main_direction[1], 1),  # 斜向方向 3
                     (-1, main_direction[1]) if start_side <= 2 else (main_direction[1], -1)])  # 斜向方向 4

    # 生成河流直到超出边界
    while 0 <= x < map_size and 0 <= y < map_size:
        if start_side != 0 and map_data[y][x] == TileType.WATER:  # 避免覆盖湖泊
            return 1

        map_data[y][x] = TileType.RIVER  # 设置当前点为河流

        direction = random.choice(directions)  # 随机选择下一个方向（倾向于主要方向）
        dx, dy = direction
        x += dx
        y += dy

    return 0

def output(map_data, set_block):
    """输出地图"""
    for row in map_data:
        for tile in row:
            print(TILE_COLORS[tile], end="")  # 设置颜色
            if set_block:
                print(f"{"■":2}", end="")  # 输出方块
            else:
                print(f"{TILE_CHARS[tile]:2}", end="")  # 输出字符
        print()  # 换行
    print(Style.RESET_ALL)  # 重置颜色

def main():
    seed = int(time.time())
    set_block = False
    map_data = generate_simplex_noise_map(seed, 41, 3)
    map_size = 41
    river_count = 5

    os.system("title MapMake")  # 更改控制台标题
    print("MapMake [版本 3.1]")
    print("Copyright(c) Harold. All rights reserved.\n")
    print("输入 '?' 查看帮助\n")

    while True:
        command = input("Command> ").strip().lower()
        match command:
            case "?" | "？":
                print("\n帮助:")
                print("generate - 生成地图")
                print("print    - 打印地图")
                print("r        - 一键生成并打印随机地图(更便捷)")
                print("data     - 显示当前参数")
                print("block    - 切换方块显示模式")
                print("map      - 设置地图尺寸")
                print("seed     - 设置种子")
                print("river    - 设置河流数目")
                print("quit     - 退出程序\n")
            case "generate":
                map_data = generate_simplex_noise_map(seed, map_size, river_count)
                print("地图已生成！\n")
            case "print":
                os.system("cls")  # 清屏
                output(map_data, set_block)  # 输出地图
            case "data":
                print(f"地图尺寸: {map_size}\n种子: {seed}")
                water_pct = int((water_max - -1) / 2 * 100)
                land_pct = int(land_max / 2 * 100)
                forest_pct = int((forest_max - land_max) / 2 * 100)
                river_pct = int((1 - forest_max) / 2 * 100)
                print(f"水、陆、森、河宽度: {water_pct}, {land_pct}, {forest_pct}, {river_pct}")
                print(f"河流参数: {river_count}\n")
            case "block":
                set_block = not set_block
                os.system("cls")
                output(map_data, set_block)
                print(f"方块显示模式: {'开启' if set_block else '关闭'}\n")
            case "map":
                try:
                    map_size = int(input(f"请输入新的地图尺寸({map_size}): "))
                    map_data = generate_simplex_noise_map(seed, map_size, river_count)
                    os.system("cls")
                    output(map_data, set_block)
                    print("尺寸已设置，地图已重新生成！\n")
                except ValueError:
                    print("错误: 尺寸必须是整数！\n")
            case "seed":
                try:
                    seed = int(input(f"请输入新种子({seed}): "))
                    map_data = generate_simplex_noise_map(seed, map_size, river_count)
                    os.system("cls")
                    output(map_data, set_block)
                    print("种子已设置，地图已重新生成！\n")
                except ValueError:
                    print("错误: 种子必须是整数！\n")
            case "river":
                try:
                    river_count = int(input(f"请输入新的河流参数({river_count}): "))
                    map_data = generate_simplex_noise_map(seed, map_size, river_count)
                    os.system("cls")
                    output(map_data, set_block)
                    print("河流参数已设置，地图已重新生成！\n")
                except ValueError:
                    print("错误: 河流参数必须是整数！\n")
            case "quit":
                print("退出程序。")
                return 0
            case "r":
                seed = int(time.time())
                if map_size <= 100:
                    river_count = random.randint(5, 12)
                else:
                    river_count = random.randint(map_size // 100 * 10, map_size // 100 * 20)
                map_data = generate_simplex_noise_map(seed, map_size, river_count)
                os.system("cls")
                output(map_data, set_block)
            case _:
                print("错误: 未知命令！输入 '?' 查看帮助。\n")

if __name__ == "__main__":
    main()
