"""
从反编译的 MTower.java 提取所有游戏数据生成 Python 文件。
用法: python convert_java_data.py <input.java> <output_dir>
"""
import re
import sys
import os


def parse_java_file(java_path):
    with open(java_path, 'r', encoding='utf-8') as f:
        source = f.read()
    return source


def _parse_value(val_str):
    """解析 Java 赋值的右值为 int。"""
    val_str = val_str.strip()
    if val_str.startswith("'"):
        # char literal: 'X', '\u0001', '\n', etc.
        inner = val_str[1:-1]
        if inner.startswith('\\u'):
            return int(inner[2:], 16)
        elif inner.startswith('\\'):
            esc_map = {'n': 10, 't': 9, 'r': 13, '\\': 92, "'": 39, '"': 34, '0': 0}
            return esc_map.get(inner[1], 0)
        elif len(inner) == 1:
            return ord(inner)
        return 0
    elif val_str.startswith('(char)') or val_str.startswith('(int)'):
        return _parse_value(val_str[val_str.index(')') + 1:])
    else:
        try:
            return int(val_str)
        except ValueError:
            return 0


def extract_map_data(source):
    """从 loadMapData() 方法提取地图数据。"""
    # 匹配 this.map[数字][数字] = 值; (值可以是数字、char literal、或带类型转换)
    rhs = r"""(?:\(char\)|\(int\)\s*)?(?:'\\u[0-9a-fA-F]{4}'|'[^']*'|-?\d+)"""
    map_pattern = re.compile(
        r'this\.map\[(\d+)\]\[(\d+)\]\s*=\s*(' + rhs + r')\s*;'
    )
    obj_pattern = re.compile(
        r'this\.mapObject\[(\d+)\]\[(\d+)\]\s*=\s*(' + rhs + r')\s*;'
    )
    
    loadmap_start = source.find('public void loadMapData()')
    if loadmap_start == -1:
        loadmap_start = source.find('public void loadMapData')
    loadmap2_start = source.find('public void loadMapData2()')
    if loadmap2_start == -1:
        loadmap2_start = source.find('public void loadMapData2')
    
    if loadmap_start == -1 or loadmap2_start == -1:
        print(f"ERROR: Cannot find loadMapData methods")
        return {}, {}
    
    loadmap_body = source[loadmap_start:loadmap2_start]
    
    map_assignments = {}
    for m in map_pattern.finditer(loadmap_body):
        row, col, val_str = int(m.group(1)), int(m.group(2)), m.group(3)
        map_assignments[(row, col)] = _parse_value(val_str)
    
    obj_assignments = {}
    for m in obj_pattern.finditer(loadmap_body):
        row, col, val_str = int(m.group(1)), int(m.group(2)), m.group(3)
        obj_assignments[(row, col)] = _parse_value(val_str)
    
    return map_assignments, obj_assignments


def extract_attribute_data(source):
    """从 loadMapData2() 提取 objectAttribute 和 mapAttribute。"""
    loadmap2_start = source.find('public void loadMapData2()')
    if loadmap2_start == -1:
        loadmap2_start = source.find('public void loadMapData2')
    
    next_method = source.find('\n    public void ', loadmap2_start + 100)
    if next_method == -1:
        next_method = len(source)
    body = source[loadmap2_start:next_method]
    
    rhs = r"""(?:\(char\)|\(int\)\s*)?(?:'\\u[0-9a-fA-F]{4}'|'[^']*'|-?\d+)"""
    obj_attr_pattern = re.compile(
        r'this\.objectAttribute\[(\d+)\]\[(\d+)\]\s*=\s*(' + rhs + r')\s*;'
    )
    map_attr_pattern = re.compile(
        r'this\.mapAttribute\[(\d+)\]\[(\d+)\]\s*=\s*(' + rhs + r')\s*;'
    )
    
    obj_attrs = {}
    for m in obj_attr_pattern.finditer(body):
        obj_id, attr_idx = int(m.group(1)), int(m.group(2))
        val = _parse_value(m.group(3))
        if obj_id not in obj_attrs:
            obj_attrs[obj_id] = {}
        obj_attrs[obj_id][attr_idx] = val
    
    map_attrs = {}
    for m in map_attr_pattern.finditer(body):
        tile_id, attr_idx = int(m.group(1)), int(m.group(2))
        val = _parse_value(m.group(3))
        if tile_id not in map_attrs:
            map_attrs[tile_id] = {}
        map_attrs[tile_id][attr_idx] = val
    
    return obj_attrs, map_attrs


def extract_messages(source):
    """提取 strMessage 数组。"""
    msg_pattern = re.compile(
        r'this\.strMessage\[(\d+)\]\[(\d+)\]\s*=\s*"((?:[^"\\]|\\.)*)"\s*;'
    )
    messages = {}
    for m in msg_pattern.finditer(source):
        lang = int(m.group(1))
        msg_id = int(m.group(2))
        text = m.group(3)
        # 处理 Java 转义
        text = text.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        if lang not in messages:
            messages[lang] = {}
        messages[lang][msg_id] = text
    return messages


def generate_map_data_py(map_assignments, obj_assignments, output_path):
    """生成 map_data.py"""
    
    # 确定哪些赋值属于哪个楼层 (floor_num -> {map: 13x13, obj: 13x13})
    floors_map = {}
    floors_obj = {}
    hidden_map = {}
    hidden_obj = {}
    
    for (row, col), val in map_assignments.items():
        floor_info = _get_floor_info(row, col)
        if floor_info is None:
            hidden_map[(row, col)] = val
            continue
        floor_num, local_row, local_col = floor_info
        if floor_num not in floors_map:
            floors_map[floor_num] = {}
        floors_map[floor_num][(local_row, local_col)] = val
    
    for (row, col), val in obj_assignments.items():
        floor_info = _get_floor_info(row, col)
        if floor_info is None:
            hidden_obj[(row, col)] = val
            continue
        floor_num, local_row, local_col = floor_info
        if floor_num not in floors_obj:
            floors_obj[floor_num] = {}
        floors_obj[floor_num][(local_row, local_col)] = val
    
    # 生成 Python 代码
    lines = []
    lines.append('# map_data.py - Auto-generated from MTower.java')
    lines.append('#')
    lines.append('# Tile types (from MAP_ATTR[type]):')
    lines.append('#   type 0 = walkable floor (includes tile values 1, 0, and stairs 4-109)')
    lines.append('#   type 1 = wall (tiles 3 = iron wall, 30-37 = border walls)')
    lines.append('#   type 2 = stairs/teleporter')
    lines.append('#')
    lines.append('# Default tile value is 1 (floor), border tiles are 30-37.')
    lines.append('#')
    lines.append('FLOOR_MAPS = {}')
    lines.append('FLOOR_OBJECTS = {}')
    lines.append('')
    
    for floor_num in sorted(set(list(floors_map.keys()) + list(floors_obj.keys()))):
        lines.append(f'def _init_floor_{floor_num}():')
        
        # Map data
        map_data = floors_map.get(floor_num, {})
        lines.append(f'    FLOOR_MAPS[{floor_num}] = [')
        for r in range(13):
            row_vals = []
            for c in range(13):
                row_vals.append(str(map_data.get((r, c), 1)))
            lines.append(f'        [{", ".join(row_vals)}],')
        lines.append(f'    ]')
        
        # Object data
        obj_data = floors_obj.get(floor_num, {})
        lines.append(f'    FLOOR_OBJECTS[{floor_num}] = [')
        for r in range(13):
            row_vals = []
            for c in range(13):
                row_vals.append(str(obj_data.get((r, c), 0)))
            lines.append(f'        [{", ".join(row_vals)}],')
        lines.append(f'    ]')
        lines.append('')
    
    # Hidden data
    if hidden_map or hidden_obj:
        lines.append('HIDDEN_MAP = {')
        for (row, col), val in sorted(hidden_map.items()):
            lines.append(f'    ({row}, {col}): {val},')
        lines.append('}')
        lines.append('')
        lines.append('HIDDEN_OBJECTS = {')
        for (row, col), val in sorted(hidden_obj.items()):
            lines.append(f'    ({row}, {col}): {val},')
        lines.append('}')
        lines.append('')
    
    # Init function
    lines.append('def init_all_floors():')
    for fn in sorted(set(list(floors_map.keys()) + list(floors_obj.keys()))):
        lines.append(f'    _init_floor_{fn}()')
    lines.append('')
    lines.append('')
    lines.append('init_all_floors()')
    lines.append('')
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated map_data.py: {len(floors_map)} floor maps, {len(hidden_map)} hidden map entries")


def _get_floor_info(row, col):
    """判断全局坐标属于哪个楼层。返回 (floor_num, local_row, local_col) 或 None。"""
    # 楼层区域: row 0-64, col 0-129 (5行 x 10列的13x13房间)
    # Floor = mapY*10 + mapX + 1
    if row >= 65 or col >= 130:
        return None
    
    map_y = row // 13
    map_x = col // 13
    local_row = row % 13
    local_col = col % 13
    
    floor_num = map_y * 10 + map_x + 1
    if floor_num < 1 or floor_num > 50:
        return None
    
    return floor_num, local_row, local_col


def generate_object_data_py(obj_attrs, map_attrs, messages, output_path):
    """生成 object_data.py"""
    lines = []
    lines.append('# object_data.py - Auto-generated from MTower.java')
    lines.append('#')
    lines.append('# Attribute indices:')
    lines.append('#   0=reserved, 1=crop1, 2=crop2, 3=type, 4=mode, 5=string,')
    lines.append('#   6=srcX, 7=srcY, 8=srcX2, 9=srcY2, 10=energy, 11=strength,')
    lines.append('#   12=defence, 13=gold, 14=item, 15=number, 16=jumpX, 17=jumpY')
    lines.append('#')
    lines.append('# Object types: 0=normal, 1=message, 3=equip, 4=item, 5=door,')
    lines.append('#   6=monster, 7=altar, 8=key, 11=score, 14=sell, 15=buy')
    lines.append('')
    
    # OBJECT_ATTR
    lines.append('OBJECT_ATTR = {')
    for obj_id in sorted(obj_attrs.keys()):
        attrs = obj_attrs[obj_id]
        row = [0] * 20
        for idx, val in attrs.items():
            if idx < 20:
                row[idx] = val
        lines.append(f'    {obj_id}: {row},')
    lines.append('}')
    lines.append('')
    
    # MAP_ATTR
    lines.append('MAP_ATTR = {')
    for tile_id in sorted(map_attrs.keys()):
        attrs = map_attrs[tile_id]
        row = [0] * 20
        for idx, val in attrs.items():
            if idx < 20:
                row[idx] = val
        lines.append(f'    {tile_id}: {row},')
    lines.append('}')
    lines.append('')
    
    # MESSAGES
    lines.append('MESSAGES = {')
    for lang in sorted(messages.keys()):
        lines.append(f'    {lang}: {{')
        for msg_id in sorted(messages[lang].keys()):
            text = messages[lang][msg_id].replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            lines.append(f'        {msg_id}: "{text}",')
        lines.append('    },')
    lines.append('}')
    lines.append('')
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated object_data.py: {len(obj_attrs)} objects, {len(map_attrs)} tiles, "
          f"{sum(len(m) for m in messages.values())} messages")


def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_java_data.py <input.java> <output_dir>")
        sys.exit(1)
    
    java_path = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading {java_path}...")
    source = parse_java_file(java_path)
    print(f"Source size: {len(source)} chars")
    
    print("Extracting map data...")
    map_assignments, obj_assignments = extract_map_data(source)
    print(f"  Map assignments: {len(map_assignments)}")
    print(f"  Object assignments: {len(obj_assignments)}")
    
    print("Extracting attribute data...")
    obj_attrs, map_attrs = extract_attribute_data(source)
    print(f"  Object attributes: {len(obj_attrs)} entries")
    print(f"  Map attributes: {len(map_attrs)} entries")
    
    print("Extracting messages...")
    messages = extract_messages(source)
    print(f"  Messages: {', '.join(f'lang {k}: {len(v)}' for k, v in messages.items())}")
    
    map_output = os.path.join(output_dir, 'map_data.py')
    obj_output = os.path.join(output_dir, 'object_data.py')
    
    print(f"Generating {map_output}...")
    generate_map_data_py(map_assignments, obj_assignments, map_output)
    
    print(f"Generating {obj_output}...")
    generate_object_data_py(obj_attrs, map_attrs, messages, obj_output)
    
    print("Done!")


if __name__ == '__main__':
    main()
