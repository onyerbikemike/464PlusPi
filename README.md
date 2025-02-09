# Amstrad 464 Plus USB Keyboard Converter

This project converts an Amstrad 464 Plus keyboard into a USB keyboard using a Pico Pi. The code scans the keyboard matrix, maps key presses to USB HID codes and sends them via the Pico Pi’s USB port.

## Features

- Scans a 10×10 keyboard matrix.
- Maps Amstrad 464 Plus key positions to USB HID key codes.
- Supports modifier keys (SHIFT, CTRL) and rollover protection.

## Hardware Requirements

- Amstrad 464 Plus keyboard.
- Pico Pi (e.g. Raspberry Pi Pico running CircuitPython).
- Appropriate wiring to connect the keyboard matrix to the Pico Pi.

The code assumes the following connections:

- **X Pins (matrix outputs):** GP15, GP14, GP13, GP12, GP11, GP10, GP9, GP8, GP7, GP6.
- **Y Pins (matrix inputs with pull-ups):** GP28, GP27, GP26, GP22, GP21, GP20, GP19, GP18, GP17, GP16.

*If you need to flip the scanning (rows ↔ columns), see the comments in the code.*

## Software Requirements

- CircuitPython installed on the Pico Pi with USB HID support enabled.

## Installation

1. Copy the code file (e.g. `keyboard_matrix.py`) to your Pico Pi’s `CIRCUITPY` drive.
2. Connect the keyboard to the Pico Pi according to the wiring above.
3. Reset the Pico Pi and the code will run automatically.

## Usage

Once installed, the Pico Pi will scan the Amstrad 464 Plus keyboard matrix and send USB HID reports to your computer. Use it as a standard USB keyboard.

## License

This project is published under the MIT License. See the license file for details.
