import pygame
import sys
import os
import socket
import time
import json
import inspect


C64_COLORS = {
    0: (0, 0, 0),        # black
    1: (255, 255, 255),  # white
    2: (136, 0, 0),      # red
    3: (170, 255, 238),  # cyan
    4: (204, 68, 204),   # purple
    5: (0, 204, 85),     # green
    6: (0, 0, 170),      # blue
    7: (238, 238, 119),  # yellow
    8: (221, 136, 85),   # orange
    9: (102, 68, 0),     # brown
    10: (255, 119, 119), # light red
    11: (51, 51, 51),    # dark grey
    12: (119, 119, 119), # grey
    13: (170, 255, 102), # light green
    14: (0, 136, 255),   # light blue
    15: (187, 187, 187), # light grey
}



pygame.init()

WIDTH, HEIGHT = 1154, 798
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("C64 screen char demo")
CLOCK = pygame.time.Clock()

BUTTON1_RECT = pygame.Rect(20, 20, 100, 40)
BUTTON2_RECT = pygame.Rect(140, 20, 100, 40)
BUTTON3_RECT = pygame.Rect(260, 20, 100, 40)
BUTTON4_RECT = pygame.Rect(380, 20, 100, 40)
BUTTON5_RECT = pygame.Rect(500, 20, 100, 40)
square_visible = False
square_color = (255, 0, 0)
square_rect = pygame.Rect(300, 200, 40, 40)

GRID_COLS, GRID_ROWS = 40, 25
bitmap = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

GRID_MARGIN_X_PCT = 0.05
GRID_MARGIN_Y_PCT = 0.1
GRID_WIDTH_PCT = 0.7
GRID_HEIGHT_PCT = 0.8

def draw_buttons():
    pygame.draw.rect(SCREEN, (200, 200, 200), BUTTON1_RECT)
    pygame.draw.rect(SCREEN, (200, 200, 200), BUTTON2_RECT)
    pygame.draw.rect(SCREEN, (200, 200, 200), BUTTON3_RECT)
    pygame.draw.rect(SCREEN, (200, 200, 200), BUTTON4_RECT)
    pygame.draw.rect(SCREEN, (200, 200, 200), BUTTON5_RECT)
    font = pygame.font.SysFont(None, 24)
    SCREEN.blit(font.render("cell bg", True, (0,0,0)), 
                (BUTTON1_RECT.x + 5, BUTTON1_RECT.y + 10))
    SCREEN.blit(font.render("sprites", True, (0,0,0)), 
                (BUTTON2_RECT.x + 5, BUTTON2_RECT.y + 10))
    SCREEN.blit(font.render("charset", True, (0,0,0)), 
                (BUTTON3_RECT.x + 5, BUTTON3_RECT.y + 10))
    SCREEN.blit(font.render("screenpage", True, (0,0,0)), 
                (BUTTON4_RECT.x + 5, BUTTON4_RECT.y + 10))
    SCREEN.blit(font.render("romcharset", True, (0,0,0)), 
                (BUTTON5_RECT.x + 5, BUTTON5_RECT.y + 10))


def draw_square():
    if square_visible:
        pygame.draw.rect(SCREEN, square_color, square_rect)












class ViceInstance:
    def __init__(self, name, port):
        self.name = name
        self.port = port







def draw_grid(current_w, current_h, grid, screen_chars=None, charset_bytes=None):
    margin_x = current_w * GRID_MARGIN_X_PCT
    margin_y = current_h * GRID_MARGIN_Y_PCT

    target_w = current_w * GRID_WIDTH_PCT
    target_h = current_h * GRID_HEIGHT_PCT

    cell_size = int(max(1, round(min(target_w / GRID_COLS, target_h / GRID_ROWS))))

    total_grid_w = GRID_COLS * cell_size
    total_grid_h = GRID_ROWS * cell_size

    grid_offset_x = int(round(current_w - margin_x - total_grid_w))
    grid_offset_y = int(round(margin_y))

    pixel_w = cell_size / 8
    pixel_h = cell_size / 8

    #print("size of chars:", screen_chars)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            px = grid_offset_x + col * cell_size
            py = grid_offset_y + row * cell_size
            rect = pygame.Rect(px, py, cell_size, cell_size)

            if screen_chars is not None and charset_bytes is not None:
                pygame.draw.rect(SCREEN, (0, 0, 0), rect)  # black background
                char_offset = 0
                index = row * GRID_COLS + col
                char_color = (0, 255, 0) # set to green as default if no color found (empty list?)
                if index < len(screen_chars):
                    char_code = screen_chars[index]
                    char_offset = char_code * 8
                    char_color = C64_COLORS.get(grid[col][row], (255, 255, 255))
                for y in range(8):
                    if char_offset + y >= len(charset_bytes):
                        continue
                    bits = charset_bytes[char_offset + y]
                    for x in range(8):
                        if bits & (0x80 >> x):
                            draw_x = int(px + x * pixel_w)
                            draw_y = int(py + y * pixel_h)
                            rect_pixel = pygame.Rect(draw_x, draw_y, int(pixel_w + 0.5), int(pixel_h + 0.5))
                            SCREEN.fill(char_color, rect_pixel)

                pygame.draw.rect(SCREEN, (30, 30, 30), rect, 1)  # cell border
            else:
                value = grid[col][row]
                color = C64_COLORS.get(value, (255, 255, 255))
                pygame.draw.rect(SCREEN, color, rect)
                pygame.draw.rect(SCREEN, (30, 30, 30), rect, 1)


def get_color_grid(context):
    cmdlabel = inspect.currentframe().f_code.co_name
    dump = send_single_command(cmdlabel, "m d021 d021")
    global_text_color = parse_single_byte_dump(dump)

    first_half = send_single_command(cmdlabel, "m d800 db5f")
    second_half = send_single_command(cmdlabel, "m db60 dbe7")
    dump_text = first_half + second_half

    grid = [[0 for _ in range(25)] for _ in range(40)]
    flat_values = []

    for line in dump_text.splitlines():
        i = 0
        while i < len(line) - 1:
            c1 = line[i]
            c2 = line[i + 1]

            if c1.upper() in "0123456789ABCDEF" and c2.upper() in "0123456789ABCDEF":
                prev_ok = i == 0 or line[i - 1] == ' '
                next_ok = i + 2 == len(line) or line[i + 2] == ' '
                if prev_ok and next_ok:
                    flat_values.append(int(c2, 16))
                    i += 2
                    continue
            i += 1

    for idx, val in enumerate(flat_values):
        row = idx // 40
        col = idx % 40
        if row < 25:
            if val == 0:
                grid[col][row] = global_text_color
            else:
                grid[col][row] = val


    return grid


def send_single_command(label, cmd_str, port=6510):
    print("[DEBUG][%s] Running command '%s'" % (label, cmd_str))

    response_text = ""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
            sock.settimeout(1)

            for _ in range(3):
                sock.sendall(b'\n')
                time.sleep(0.5)

            try:
                sock.recv(4096)
            except socket.timeout:
                pass

            sock.sendall((cmd_str + "\n").encode("ascii"))

            response = b""
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except socket.timeout:
                    break

            response_text = response.decode(errors="ignore")
            print("[DEBUG][%s] Response:\n%s" % (label, response_text))
            time.sleep(0.1)

    except Exception as e:
        print("[ERROR] communication failed: %s" % e)

    return response_text


def parse_vice_memory_dump(dump_text):
    grid = [[0 for _ in range(25)] for _ in range(40)]
    flat_values = []

    for line in dump_text.splitlines():
        i = 0
        while i < len(line) - 1:
            c1 = line[i]
            c2 = line[i + 1]

            if c1.upper() in "0123456789ABCDEF" and c2.upper() in "0123456789ABCDEF":
                prev_ok = i == 0 or line[i - 1] == ' '
                next_ok = i + 2 == len(line) or line[i + 2] == ' '
                if prev_ok and next_ok:
                    flat_values.append(int(c2, 16))
                    i += 2
                    continue
            i += 1

    for idx, val in enumerate(flat_values):
        row = idx // 40
        col = idx % 40
        if row < 25:
            grid[col][row] = val

    return grid


def get_all_sprites(context):
    cmdlabel = inspect.currentframe().f_code.co_name
    dump = send_single_command(cmdlabel, "m dd00 dd00")
    dd00_val = parse_single_byte_dump(dump)


    VIC_BANK_BASE = [0xC000, 0x8000, 0x4000, 0x0000]
    vic_bank = dd00_val & 3
    vic_base = VIC_BANK_BASE[vic_bank]

    dump = send_single_command(cmdlabel, "m d015 d015")
    d015_val = parse_single_byte_dump(dump)

    ptr_base = 0x07F8
    dump = send_single_command(cmdlabel,
                               f"m {ptr_base:x} {ptr_base+7:x}")
    sprite_ptrs = parse_flat_hex_bytes(dump)

    sprites = []

    for i, ptr in enumerate(sprite_ptrs):
        if ((d015_val >> i) & 1) == 0:
            continue
        sprite_addr = vic_base + (ptr << 6)
        dump = send_single_command(cmdlabel,
                                   f"m {sprite_addr:x} {sprite_addr+63:x}")
        sprite_bytes = parse_flat_hex_bytes(dump)
        sprites.append({
            "index": i,
            "addr": sprite_addr,
            "bytes": sprite_bytes
        })

    return sprites, vic_bank


def show_all_sprites(screen, sprites, font, scale=4):
    clear_x = 0
    clear_y = screen.get_height() - 21 * scale - 40
    clear_w = screen.get_width()
    clear_h = 21 * scale + 60
    screen.fill((0, 0, 0), pygame.Rect(clear_x, clear_y, clear_w, clear_h))

    x_offset = 10
    base_y = screen.get_height() - 21 * scale - 10

    for s in sprites:
        text_surf = font.render(f"{s['index']}: ${s['addr']:04X}", True, (255,255,255))
        screen.blit(text_surf, (x_offset, base_y - 20))

        sprite_bytes = s["bytes"]

        for row in range(21):
            for block in range(3):
                byte_index = row*3 + block
                if byte_index >= len(sprite_bytes):
                    continue
                b = sprite_bytes[byte_index]
                for bit in range(8):
                    if (b >> (7 - bit)) & 1:
                        px = x_offset + (block*8 + bit) * scale
                        py = base_y + row * scale
                        rect = pygame.Rect(px, py, scale, scale)
                        pygame.draw.rect(screen, (255,255,0), rect)

        x_offset += 24 * scale + 30


def get_screen_chars(context):
    cmdlabel = inspect.currentframe().f_code.co_name

    # decode dd00 and map bank position to hex addr
    dump = send_single_command(cmdlabel, "m dd00 dd00")
    dd00_val = parse_single_byte_dump(dump)
    vic_bank = (~dd00_val) & 0x03
    vic_bank_base = [0x0000, 0x4000, 0x8000, 0xC000][vic_bank]

    dump = send_single_command(cmdlabel, "m d018 d018")
    d018_val = parse_single_byte_dump(dump)

    # screen page = bits 4-7 (upper nibble)
    screen_page = (d018_val >> 4) & 0x0F

    # final screen address
    screen_base = vic_bank_base + screen_page * 0x400
    screen_size = 40 * 25

    dump_bytes = send_single_command(
        cmdlabel,
        f"m {screen_base:04x} {screen_base + screen_size - 1:04x}"
    )

    screen_chars = parse_flat_hex_bytes(dump_bytes)
    return screen_chars, screen_base, vic_bank


def get_full_charset(context):
    cmdlabel = inspect.currentframe().f_code.co_name

    # decode dd00 and map bank position to hex addr
    dump_dd00 = send_single_command(cmdlabel, "m dd00 dd00")
    dd00_val = parse_single_byte_dump(dump_dd00)
    VIC_BANK_BASE = [0xC000, 0x8000, 0x4000, 0x0000]
    vic_bank_index = dd00_val & 3
    vic_base = VIC_BANK_BASE[vic_bank_index]

    # d018 bits 1, 2, and 3 select which 2k offset
    dump_d018 = send_single_command(cmdlabel, "m d018 d018")
    d018_val = parse_single_byte_dump(dump_d018)
    char_offset_2k = (d018_val >> 1) & 0b111
    
    # character start pos in mem = 16K base addr + 2K offset * 2048
    charset_base = vic_base + (char_offset_2k * 0x0800)
    charset_size = 256 * 8

    dump_bytes = send_single_command(
        cmdlabel,
        f"m {charset_base:04x} {charset_base + charset_size - 1:04x}"
    )
    charset_all_bytes = parse_flat_hex_bytes(dump_bytes)
    
    return charset_all_bytes, vic_base , vic_bank_index


def get_rom_charset(context):
    cmdlabel = inspect.currentframe().f_code.co_name
    setrombank = send_single_command(cmdlabel, "bank rom")
    charset_base = 0xD000
    charset_size = 256 * 8  # 256 chars 8 bytes each

    dump_bytes = send_single_command(
        cmdlabel,
        f"m {charset_base:04x} {charset_base + charset_size - 1:04x}"
    )
    setrombank = send_single_command(cmdlabel, "bank cpu")
    charset_all_bytes = parse_flat_hex_bytes(dump_bytes)
    return charset_all_bytes


def update_scrollable_list(event_list, screen, rect, items, scroll_y, selected_index, font):
    item_height = font.get_linesize() + 6
    content_height = len(items) * item_height
    content_surface = pygame.Surface((rect.width, content_height))
    
    # takes the mouse event and handles a click or scroll
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                mx, my = event.pos
                rel_y = my - rect.top + scroll_y
                index = rel_y // item_height
                if 0 <= index < len(items):
                    selected_index = index
                    print(items[selected_index])
        elif event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos):
                scroll_y -= event.y * 20
                scroll_y = max(0, min(scroll_y, max(content_height - rect.height, 0)))

    # draw text in the scroll box
    content_surface.fill((240, 240, 240))
    for i, p in enumerate(items):
        color = (255, 0, 0) if i == selected_index else (0, 0, 0)
        text_surf = font.render(p, True, color)
        content_surface.blit(text_surf, (2, i * item_height))

    # refresh the area inside the scrollbox viewport
    screen.blit(content_surface, rect.topleft, area=pygame.Rect(0, scroll_y, rect.width, rect.height))
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    return scroll_y, selected_index


def show_full_charset(screen, all_bytes, font, scale=2, chars_per_row=16):
    for char_code in range(256):
        # get 8 bytes for 1 char bitmap
        char_bytes = all_bytes[char_code*8 : char_code*8 + 8]

        # set up like a bitmap to draw in pygame
        row_index = char_code // chars_per_row
        col_index = char_code % chars_per_row
        base_x = 10 + col_index * 8 * scale
        base_y = 110 + row_index * 8 * scale

        for row in range(8):
            byte = char_bytes[row]
            for bit in range(8):
                if (byte >> (7 - bit)) & 1:
                    px = base_x + bit * scale
                    py = base_y + row * scale
                    rect = pygame.Rect(px, py, scale, scale)
                    pygame.draw.rect(screen, (0, 255, 0), rect)




def parse_single_byte_dump(dump_text):
    for line in dump_text.splitlines():
        line = line.strip()
        if not line or not line.startswith('>C:'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            byte_str = parts[1]  # operate on one byte
            try:
                return int(byte_str, 16)
            except ValueError:
                pass
    return 0


def parse_flat_hex_bytes(dump_text):
    flat_values = []
    for line in dump_text.splitlines():
        line = line[8:]  # discard first 8
        tokens = line.split()[:16]  # take only first 16 hex pairs
        for token in tokens:
            # only accept pairs of 2 hex digits as values
            if len(token) == 2 and all(c in "0123456789ABCDEFabcdef" for c in token):
                flat_values.append(int(token, 16))
    #print(len(flat_values), "DEBUG: output\n", flat_values)
    return flat_values


def update_text_inputs(events, screen, font, boxes, state):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            for box in boxes:
                box["active"] = box["rect"].collidepoint(event.pos)
                if "save_rect" in box and box["save_rect"].collidepoint(event.pos):
                    box["saved"] = True
                    print(f"Saved: {box.get('text', '')}")
                    filename=box.get('text')
                    my_save_function(state, filename)
                if "load_rect" in box and box["load_rect"].collidepoint(event.pos):
                    fileindexpos = state.get("scroll_selected", -1)
                    files = state.get("files", [])
                    if 0 <= fileindexpos < len(files):
                        filename = files[fileindexpos]
                        print("Load clicked for:", filename)
                        my_load_function(state, filename)
                    else:
                        print("No file selected")
        elif event.type == pygame.KEYDOWN:
            for box in boxes:
                if box.get("active"):
                    if event.key == pygame.K_BACKSPACE:
                        box["text"] = box.get("text", "")[:-1]
                    elif event.key == pygame.K_RETURN:
                        box["saved"] = True
                        print(f"Saved: {box.get('text', '')}")
                    else:
                        box["text"] = box.get("text", "") + event.unicode

    for box in boxes:
        color = (255, 255, 255) if box.get("active") else (180, 180, 180)
        pygame.draw.rect(screen, color, box["rect"], 2)
        txt_surf = font.render(box.get("text", ""), True, (255, 255, 255))
        screen.blit(txt_surf, (box["rect"].x + 5, box["rect"].y + 2))
        
        if "save_rect" in box:
            pygame.draw.rect(screen, (100, 200, 100), box["save_rect"])
            save_txt = font.render("Save", True, (0, 0, 0))
            screen.blit(save_txt, (box["save_rect"].x + 5, box["save_rect"].y + 2))

        if "load_rect" in box:
            pygame.draw.rect(screen, (100, 100, 200), box["load_rect"])
            load_txt = font.render("Load", True, (0, 0, 0))
            screen.blit(load_txt, (box["load_rect"].x + 5, box["load_rect"].y + 2))
        
    return boxes


def my_save_functionold(state, filename):
    if not filename.endswith(".out"):
        filename = filename + ".out"
    with open(filename, "w") as f:
        json.dump(state, f)


def my_save_function(state, filename):
    if not filename.endswith(".out"):
        filename = filename + ".out"
    with open(filename, "w") as f:
        json.dump(state, f)

    save_screen_chararray(filename, 
                          state.get("charset"), 
                          state.get("screen_chars"), 
                          state.get("fullgrid"))
    

def my_load_function(state, filename):
    with open(filename, "r") as f:
        loaded = json.load(f)
    state.clear()
    state.update(loaded)




def save_screen_chararray_old(filename, charset, screen_chars, fullgrid):
    out_filename = f"{filename}_char.txt"
    with open(out_filename, "w") as f:
        def write_array(name, data):
            f.write(f"unsigned char {name}[] = {{\n")
            flat_data = []
            for item in data:
                if isinstance(item, list):
                    flat_data.extend(item)
                else:
                    flat_data.append(item)

            for i, val in enumerate(flat_data):
                f.write(f"0x{val:02X}")
                if i != len(flat_data) - 1:
                    f.write(",")
                if (i + 1) % 8 == 0:
                    f.write("\n")
                else:
                    f.write(" ")
            f.write("\n};\n\n")


        if charset is not None:
            write_array("chars", charset)
        if screen_chars is not None:
            write_array("screen_chars", screen_chars)
        if fullgrid is not None:
            write_array("fullgrid", fullgrid)


def save_screen_chararray(filename, charset, screen_chars, fullgrid):
    out_filename = f"{filename}_char.txt"
    
    with open(out_filename, "w") as f:
        
        def write_array(name, data):
            f.write(f"unsigned char {name}[] = {{\n")
            flat_data = []
            
            for item in data:
                if isinstance(item, list):
                    flat_data.extend(item)
                else:
                    flat_data.append(item)

            for i, val in enumerate(flat_data):
                f.write(f"0x{val:02X}")
                
                if i != len(flat_data) - 1:
                    f.write(",")
                
                if (i + 1) % 8 == 0:
                    f.write("\n")
                elif i != len(flat_data) - 1:
                    f.write(" ")
            
            f.write("};\n\n")
            for i, row in enumerate(fullgrid):
                row_cols = len(row)
                
                #print(f"Row {i:02d} (Index {i}): {row_cols} columns wide.")

        if charset is not None:
            write_array("chars", charset)
        if screen_chars is not None:
            write_array("screen_chars", screen_chars)
        if fullgrid is not None:
            transposed_fullgrid = [list(col) for col in zip(*fullgrid)]
            write_array("color_ram", transposed_fullgrid)






context = {"instance": ViceInstance("instance", 6510)}

sprites = None
charset_all_bytes = None
fullgridoutput = None
screen_chars = None
scroll_y = 0
viewport1 = pygame.Rect(20, 500, 150, 100)
scroll1 = 0
selected1 = None




text_boxesold = [ #save boxes on screen
    {"rect": pygame.Rect(20, 500, 100, 30), "text": "", "active": False,
     "save_rect": pygame.Rect(110, 320, 60, 30), "saved": False},  # left box
]


text_boxes = [
    {"rect": pygame.Rect(20, 470, 100, 30), "text": "", "active": False,
     "save_rect": pygame.Rect(110, 470, 60, 30), "saved": False},  # top
         
    {"rect": pygame.Rect(50, 430, 60, 30),
     "text": "",
     "active": False,
     "saved": False,
     "load_rect": pygame.Rect(50, 430, 60, 30)}
]



def get_out_files(path):
    files = []
    for name in os.listdir(path):
        if name.endswith(".out"):
            files.append(name)
    return files




global_vars = {
    "fullgrid": None,
    "sprites": None,
    "sprite_bank": None,
    "charset": None,
    "vic_bank": None,
    "screen_chars": None,
    "screen_base": None,
    "scroll_selected": 0, # index pos of "files"
    "files": None
}




grid1 = [[0 for _ in range(25)] for _ in range(40)]

font = pygame.font.SysFont("Consolas", 20)


while True:
    events = pygame.event.get()
    for event in events:
        global_vars["files"] = get_out_files(".")

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            print(WIDTH, HEIGHT)
            SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if BUTTON1_RECT.collidepoint(event.pos):
                global_vars["fullgrid"] = get_color_grid(context)
            elif BUTTON2_RECT.collidepoint(event.pos):
                sprites, bank = get_all_sprites(context)
                global_vars["sprites"] = sprites
                global_vars["sprite_bank"] = bank
            elif BUTTON3_RECT.collidepoint(event.pos):
                charset_all_bytes, vic_bank, banknum = get_full_charset(context)
                global_vars["charset"] = charset_all_bytes
            elif BUTTON4_RECT.collidepoint(event.pos):
                screen_chars, screen_base, banknum = get_screen_chars(context)
                global_vars["screen_chars"] = screen_chars
                global_vars["screen_base"] = screen_base
                global_vars["vic_bank"] = banknum
            elif BUTTON5_RECT.collidepoint(event.pos):
                global_vars["charset"] = get_rom_charset(context)

                



    viewport_rect = pygame.Rect(50, 150, 300, 200)
    SCREEN.fill((0, 0, 0))
    draw_buttons()
    #draw_square()
    
    if global_vars["fullgrid"] is not None:
        draw_grid(WIDTH, HEIGHT,
                global_vars["fullgrid"],
                screen_chars=global_vars["screen_chars"],
                charset_bytes=global_vars["charset"])

    if global_vars["sprites"] is not None:
        show_all_sprites(SCREEN, global_vars["sprites"], font)

    if global_vars["charset"] is not None:
        #print("got charset", global_vars["charset"])
        show_full_charset(SCREEN, global_vars["charset"], font)


    selected1 = global_vars["scroll_selected"]
    scroll1, selected_index = update_scrollable_list(events, SCREEN, viewport1,
                                                global_vars["files"], scroll1, selected1, font)
    
    global_vars["scroll_selected"] = selected_index
    #scroll2, selected2 = update_scrollable_list(events, SCREEN, viewport2,
    #                                            prefixes2, scroll2, selected2, font)
    
    text_boxes = update_text_inputs(events, SCREEN, font, text_boxes, global_vars)


    vic_text = f"VIC Bank: {global_vars.get('vic_bank', 'N/A')}"
    text_surf = font.render(vic_text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(topright=(SCREEN.get_width() - 10, 10))
    SCREEN.blit(text_surf, text_rect)
    #print(vic_text)
    

    pygame.display.flip()
    CLOCK.tick(5)