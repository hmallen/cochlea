import i2c_lcd_driver
import time


if __name__ == '__main__':
    lcd_screen = i2c_lcd_driver.lcd()

    lcd_screen.lcd_display_string('Hello, world!', 1)

    str_pad = ' ' * 16
    display_string = str_pad + 'Hello, world! Making longer to scroll.'

    while True:
        for x in range(0, len(display_string)):
            display_text = display_string[x:(x+16)]
            lcd_screen.lcd_display_string(display_text, 2)
            time.sleep(0.15)
            #lcd_screen.lcd_display_string(str_pad, 2)
