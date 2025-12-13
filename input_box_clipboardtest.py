import pygame
import pyperclip
import textwrap
import lz4.block

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Text Paste, Copy, and Clear Example")

INPUT_RECT = pygame.Rect(50, 50, 300, 300)
OUTPUT_RECT = pygame.Rect(450, 50, 300, 300)
COPY_BUTTON_RECT = pygame.Rect(OUTPUT_RECT.left + 100, OUTPUT_RECT.top - 30, 100, 25)
CLEAR_BUTTON_RECT = pygame.Rect(INPUT_RECT.left + 100, INPUT_RECT.top - 30, 100, 25)

BG_COLOR = (30, 30, 30)
INPUT_COLOR = (50, 50, 150)
OUTPUT_COLOR = (50, 150, 50)
BUTTON_COLOR = (200, 200, 50)
BUTTON_HOVER_COLOR = (255, 255, 100)
TEXT_COLOR = (255, 255, 255)
FONT = pygame.font.SysFont(None, 24)

input_active = False
input_text = ""
output_lines = []


# Compress the data using LZ4


# Compute sizes
#compressed_size = len(compressed_data)
#compression_ratio = (compressed_size / output_data_size) * 100 if input_size > 0 else 0

from PIL import Image

def png_to_c_array(path, array_name="sprite"):
    img = Image.open(path).convert("1")  # convert to 1-bit (black & white)
    if img.size != (21, 24):
        raise ValueError("Image must be 21x24 pixels")
    pixels = list(img.getdata())
    data = []
    for y in range(24):
        row = 0
        bit_count = 0
        for x in range(21):
            pixel = pixels[y * 21 + x]
            bit = 0 if pixel == 0 else 1
            row = (row << 1) | bit
            bit_count += 1
            if bit_count == 8:
                data.append(row)
                row = 0
                bit_count = 0
        if bit_count > 0:
            row <<= (8 - bit_count)  # pad remaining bits
            data.append(row)
    # Generate C array string
    c_array = f"const unsigned char {array_name}[] = {{\n    "
    for i, byte in enumerate(data):
        c_array += f"0x{byte:02X}, "
        if (i + 1) % 12 == 0:
            c_array += "\n    "
    c_array = c_array.rstrip(", ") + "\n};"
    return c_array


def render_text_box(rect, text_lines):
    pygame.draw.rect(screen, OUTPUT_COLOR, rect)
    y = rect.top + 5
    for line in text_lines:
        rendered = FONT.render(line, True, TEXT_COLOR)
        screen.blit(rendered, (rect.left + 5, y))
        y += FONT.get_height() + 2

def wrap_text(text, font, max_width):
    words = text.replace('\n', ' \n ').split()
    lines = []
    current_line = ""
    for word in words:
        if word == '\n':
            lines.append(current_line)
            current_line = ""
            continue
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width - 10:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

running = True
while running:
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, INPUT_COLOR, INPUT_RECT)
    render_text_box(OUTPUT_RECT, output_lines)

    # Draw copy button
    mouse_pos = pygame.mouse.get_pos()
    copy_color = BUTTON_HOVER_COLOR if COPY_BUTTON_RECT.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, copy_color, COPY_BUTTON_RECT)
    copy_text = FONT.render("Copy All", True, (0, 0, 0))
    screen.blit(copy_text, (COPY_BUTTON_RECT.left + 10, COPY_BUTTON_RECT.top + 3))

    # Draw clear button
    clear_color = BUTTON_HOVER_COLOR if CLEAR_BUTTON_RECT.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, clear_color, CLEAR_BUTTON_RECT)
    clear_text = FONT.render("Clear", True, (0, 0, 0))
    screen.blit(clear_text, (CLEAR_BUTTON_RECT.left + 20, CLEAR_BUTTON_RECT.top + 3))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if INPUT_RECT.collidepoint(event.pos):
                input_active = True
            else:
                input_active = False
            if COPY_BUTTON_RECT.collidepoint(event.pos):
                pyperclip.copy("\n".join(output_lines))
            if CLEAR_BUTTON_RECT.collidepoint(event.pos):
                input_text = ""
                output_lines = []
        elif event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                pasted = pyperclip.paste()
                input_text += pasted
            elif event.unicode and event.key != pygame.K_v:
                input_text += event.unicode
            output_lines = wrap_text(input_text, FONT, OUTPUT_RECT.width)
        elif event.type == pygame.DROPFILE:
            dropped_file = event.file  # full path of the dragged file
            #arraytext = png_to_c_array(dropped_file, "sprite1")
            compressed_data = lz4.block.compress(
            bytes(dropped_file),       # input to compress
            mode='high_compression',  # Enables maximum compression mode
            store_size=False          # Prevents storing original size (reduces overhead)
            )
            #input_text += dropped_file
            output_lines = wrap_text(compressed_data, FONT, OUTPUT_RECT.width)
            print(dropped_file)


    input_surface = FONT.render(input_text, True, TEXT_COLOR)
    screen.blit(input_surface, (INPUT_RECT.left + 5, INPUT_RECT.top + 5))
    pygame.display.flip()

pygame.quit()
