import time
import board
import digitalio
import usb_hid

DEBOUNCE_DELAY_MS = 20

# Setup X pins as inputs with pull-ups (was outputs)
x_pin_nums = [board.GP15, board.GP14, board.GP13, board.GP12, board.GP11,
              board.GP10, board.GP9, board.GP8, board.GP7, board.GP6]
x_pins = []
for num in x_pin_nums:
    pin = digitalio.DigitalInOut(num)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    x_pins.append(pin)

# Setup Y pins as outputs (was inputs)
y_pin_nums = [board.GP28, board.GP27, board.GP26, board.GP22, board.GP21,
              board.GP20, board.GP19, board.GP18, board.GP17, board.GP16]
y_pins = []
for num in y_pin_nums:
    pin = digitalio.DigitalInOut(num)
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = True
    y_pins.append(pin)

# Define key mapping (matrix coordinates are 1-indexed)
key_entries = [
    {"x":10, "y":9,  "unshifted": "UP ARROW",     "shifted": ""},
    {"x":9,  "y":9,  "unshifted": "LEFT ARROW",   "shifted": ""},
    {"x":8,  "y":9,  "unshifted": "BACKSPACE",    "shifted": ""},
    {"x":7,  "y":9,  "unshifted": "^",            "shifted": "£"},
    {"x":6,  "y":9,  "unshifted": "0",            "shifted": "_"},
    {"x":5,  "y":9,  "unshifted": "8",            "shifted": "("},
    {"x":4,  "y":9,  "unshifted": "6",            "shifted": "&"},
    {"x":3,  "y":9,  "unshifted": "4",            "shifted": "$"},
    {"x":2,  "y":9,  "unshifted": "1",            "shifted": "!"},
    
    {"x":10, "y":8,  "unshifted": "RIGHT ARROW",  "shifted": ""},
    {"x":9,  "y":8,  "unshifted": "COPY",         "shifted": ""},
    {"x":8,  "y":8,  "unshifted": "[",            "shifted": "{"},
    {"x":7,  "y":8,  "unshifted": "=",            "shifted": "-"},
    {"x":6,  "y":8,  "unshifted": "9",            "shifted": ")"},
    {"x":5,  "y":8,  "unshifted": "7",            "shifted": "'"},
    {"x":4,  "y":8,  "unshifted": "5",            "shifted": "%"},
    {"x":3,  "y":8,  "unshifted": "3",            "shifted": "#"},
    {"x":2,  "y":8,  "unshifted": "2",            "shifted": "\""},
    
    {"x":10, "y":7,  "unshifted": "DOWN ARROW",   "shifted": ""},
    {"x":9,  "y":7,  "unshifted": "F7",           "shifted": ""},
    {"x":8,  "y":7,  "unshifted": "RETURN",       "shifted": ""},
    {"x":7,  "y":7,  "unshifted": "@",            "shifted": "|"},
    {"x":6,  "y":7,  "unshifted": "o",            "shifted": "O"},
    {"x":5,  "y":7,  "unshifted": "u",            "shifted": "U"},
    {"x":4,  "y":7,  "unshifted": "r",            "shifted": "R"},
    {"x":3,  "y":7,  "unshifted": "e",            "shifted": "E"},
    {"x":2,  "y":7,  "unshifted": "ESC",          "shifted": ""},
    
    {"x":10, "y":6,  "unshifted": "F9",           "shifted": ""},
    {"x":9,  "y":6,  "unshifted": "F8",           "shifted": ""},
    {"x":8,  "y":6,  "unshifted": "]",            "shifted": "}"},
    {"x":7,  "y":6,  "unshifted": "p",            "shifted": "P"},
    {"x":6,  "y":6,  "unshifted": "i",            "shifted": "I"},
    {"x":5,  "y":6,  "unshifted": "y",            "shifted": "Y"},
    {"x":4,  "y":6,  "unshifted": "t",            "shifted": "T"},
    {"x":3,  "y":6,  "unshifted": "w",            "shifted": "W"},
    {"x":2,  "y":6,  "unshifted": "q",            "shifted": "Q"},
    
    {"x":10, "y":5,  "unshifted": "F6",           "shifted": ""},
    {"x":9,  "y":5,  "unshifted": "F5",           "shifted": ""},
    {"x":8,  "y":5,  "unshifted": "F4",           "shifted": ""},
    {"x":7,  "y":5,  "unshifted": ";",            "shifted": "+"},
    {"x":6,  "y":5,  "unshifted": "l",            "shifted": "L"},
    {"x":5,  "y":5,  "unshifted": "h",            "shifted": "H"},
    {"x":4,  "y":5,  "unshifted": "g",            "shifted": "G"},
    {"x":3,  "y":5,  "unshifted": "s",            "shifted": "S"},
    {"x":2,  "y":5,  "unshifted": "TAB",          "shifted": ""},
    
    {"x":10, "y":4,  "unshifted": "F3",           "shifted": ""},
    {"x":9,  "y":4,  "unshifted": "F1",           "shifted": ""},
    {"x":8,  "y":4,  "unshifted": "SHIFT",        "shifted": ""},
    {"x":7,  "y":4,  "unshifted": ":",            "shifted": "*"},
    {"x":6,  "y":4,  "unshifted": "k",            "shifted": "K"},
    {"x":5,  "y":4,  "unshifted": "j",            "shifted": "J"},
    {"x":4,  "y":4,  "unshifted": "f",            "shifted": "F"},
    {"x":3,  "y":4,  "unshifted": "d",            "shifted": "D"},
    {"x":2,  "y":4,  "unshifted": "a",            "shifted": "A"},
    
    {"x":10, "y":3,  "unshifted": "ENTER",        "shifted": ""},
    {"x":9,  "y":3,  "unshifted": "F2",           "shifted": ""},
    {"x":8,  "y":3,  "unshifted": "\\",           "shifted": "'"},
    {"x":7,  "y":3,  "unshifted": "/",            "shifted": "?"},
    {"x":6,  "y":3,  "unshifted": "m",            "shifted": "M"},
    {"x":5,  "y":3,  "unshifted": "n",            "shifted": "N"},
    {"x":4,  "y":3,  "unshifted": "b",            "shifted": "B"},
    {"x":3,  "y":3,  "unshifted": "c",            "shifted": "C"},
    {"x":2,  "y":3,  "unshifted": "CAPS LOCK",    "shifted": ""},
    
    {"x":10, "y":2,  "unshifted": ".",            "shifted": ""},
    {"x":9,  "y":2,  "unshifted": "F0",           "shifted": ""},
    {"x":8,  "y":2,  "unshifted": "CTRL",         "shifted": ""},
    {"x":7,  "y":2,  "unshifted": ".",            "shifted": ">"},
    {"x":6,  "y":2,  "unshifted": ",",            "shifted": "<"},
    {"x":5,  "y":2,  "unshifted": "SPACE",        "shifted": ""},
    {"x":4,  "y":2,  "unshifted": "v",            "shifted": "V"},
    {"x":3,  "y":2,  "unshifted": "x",            "shifted": "X"},
    {"x":2,  "y":2,  "unshifted": "z",            "shifted": "Z"},
    
    {"x":1,  "y":2,  "unshifted": "DELETE",       "shifted": ""}
]

def lookup_key_entry(x, y):
    for entry in key_entries:
        if entry["x"] == x and entry["y"] == y:
            return entry
    return None

def get_hid_code(label):
    mod = 0
    if label == "SHIFT":
        return 0x02, 0
    if label == "CTRL":
        return 0x01, 0
    if label == "CAPS LOCK":
        return 0, 0x39
    if label == "UP ARROW":
        return 0, 0x52
    if label == "DOWN ARROW":
        return 0, 0x51
    if label == "LEFT ARROW":
        return 0, 0x50
    if label == "RIGHT ARROW":
        return 0, 0x4F
    if label == "BACKSPACE":
        return 0, 0x2A
    if label == "TAB":
        return 0, 0x2B
    if label in ["ENTER", "RETURN"]:
        return 0, 0x28
    if label == "ESC":
        return 0, 0x29
    if label == "SPACE":
        return 0, 0x2C
    if label == "DELETE":
        return 0, 0x4C
    if label.startswith("F"):
        try:
            num = int(label[1:])
            if num == 0:
                return 0, 0x43
            elif 1 <= num <= 9:
                return 0, 0x39 + num
        except:
            pass
    if len(label) == 1:
        c = label
        if 'a' <= c <= 'z':
            return 0, 0x04 + (ord(c) - ord('a'))
        if 'A' <= c <= 'Z':
            return 0x02, 0x04 + (ord(c) - ord('A'))
        if '1' <= c <= '9':
            return 0, 0x1E + (ord(c) - ord('1'))
        if c == '0':
            return 0, 0x27
        mapping = {
            '-':0x2D, '=':0x2E, '[':0x2F, ']':0x30, '\\':0x31,
            ';':0x33, "'":0x34, '`':0x35, ',':0x36, '.':0x37, '/':0x38,
            '^':0x23, '$':0x21, '&':0x24, '(':0x26, ')':0x27,
            '_':0x2D, '*':0x25, ':':0x33, '>':0x37, '<':0x36,
            '@':0x1F, '|':0x31, '+':0x2E, '"':0x1F, '!':0x1E,
            '#':0x20, '%':0x22, '{':0x2F, '}':0x30, '?':0x38,
            '£':0x20  # Added for £
        }
        if c in mapping:
            code = mapping[c]
            if c in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                     '_', '+', '{', '}', '|', ':', '"', '<', '>', '?', '£'] or ('A' <= c <= 'Z'):
                mod = 0x02
            return mod, code
    return 0, 0

def send_hid_report(modifier, keys):
    report = bytearray(8)
    report[0] = modifier
    for i in range(min(len(keys), 6)):
        report[2 + i] = keys[i]
    usb_hid.devices[0].send_report(report)

def scan_matrix():
    # Scan using Y outputs and X inputs; build a temporary matrix [y][x]
    temp_state = [[False for _ in x_pins] for _ in y_pins]
    for j, y in enumerate(y_pins):
        y.value = False
        time.sleep(5e-6)
        for i, x in enumerate(x_pins):
            temp_state[j][i] = not x.value
        y.value = True
    # Transpose so that state[row][col] corresponds to X then Y (as per key mapping)
    state = [[temp_state[j][i] for j in range(len(y_pins))] for i in range(len(x_pins))]
    return state

def matrix_equal(a, b):
    for i in range(len(a)):
        for j in range(len(a[0])):
            if a[i][j] != b[i][j]:
                return False
    return True

last_state = [[False for _ in y_pins] for _ in x_pins]

while True:
    state = scan_matrix()
    time.sleep(DEBOUNCE_DELAY_MS / 1000.0)
    verify_state = scan_matrix()
    if not matrix_equal(state, verify_state):
        time.sleep(5 / 1000.0)
        continue

    if not matrix_equal(state, last_state):
        last_state = [row[:] for row in state]
        modifier = 0
        keycodes = []
        global_shift = False

        # First pass: check for modifiers
        for i in range(len(x_pins)):
            for j in range(len(y_pins)):
                if state[i][j]:
                    entry = lookup_key_entry(i + 1, j + 1)
                    if entry:
                        if entry["unshifted"] == "SHIFT":
                            global_shift = True
                            modifier |= 0x02
                        if entry["unshifted"] == "CTRL":
                            modifier |= 0x01

        # Second pass: process non-modifier keys
        rollover = False
        for i in range(len(x_pins)):
            for j in range(len(y_pins)):
                if state[i][j]:
                    entry = lookup_key_entry(i + 1, j + 1)
                    if not entry or entry["unshifted"] in ["SHIFT", "CTRL"]:
                        continue
                    label = entry["shifted"] if global_shift and entry["shifted"] != "" else entry["unshifted"]
                    local_mod, code = get_hid_code(label)
                    modifier |= local_mod
                    if code:
                        if len(keycodes) < 6:
                            keycodes.append(code)
                        else:
                            keycodes = [1]
                            rollover = True
                            break
            if rollover:
                break

        send_hid_report(modifier, keycodes)
    time.sleep(5 / 1000.0)
