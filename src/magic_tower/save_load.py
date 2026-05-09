import struct
import os


SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "savedat")


def _ensure_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def save_game(game, slot):
    _ensure_dir()
    path = os.path.join(SAVE_DIR, f"data{slot}.dat")

    game._set_hidden_state()

    with open(path, "wb") as f:
        for y in range(78):
            for x in range(130):
                val = game.obj_data[y][x]
                f.write(struct.pack(">H", val & 0xFFFF))
        for y in range(78):
            for x in range(130):
                val = game.map_data[y][x]
                f.write(struct.pack(">H", val & 0xFFFF))


def load_game(game, slot):
    path = os.path.join(SAVE_DIR, f"data{slot}.dat")
    if not os.path.exists(path):
        return False

    with open(path, "rb") as f:
        data = f.read()

    expected = 78 * 130 * 2 * 2
    if len(data) < expected:
        return False

    offset = 0
    for y in range(78):
        for x in range(130):
            game.obj_data[y][x] = struct.unpack_from(">H", data, offset)[0]
            offset += 2
    for y in range(78):
        for x in range(130):
            game.map_data[y][x] = struct.unpack_from(">H", data, offset)[0]
            offset += 2

    game._restore_hidden_state()
    return True


def has_save(slot):
    path = os.path.join(SAVE_DIR, f"data{slot}.dat")
    return os.path.exists(path)
