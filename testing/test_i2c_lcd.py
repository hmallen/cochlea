import i2c_lcd_driver
import time


if __name__ == '__main__':
    lcd_screen = i2c_lcd_driver.lcd()

    lcd_screen.lcd_display_string('Hello, world!', 1)

    str_pad = ' ' * 16
    display_string = str_pad + 'Hello, world! Making longer to scroll.' + str_pad

    for x in range(0, (len(display_string) - 16)):
        display_text = display_string[x:(x+16)]
        lcd_screen.lcd_display_string(display_text, 2)
        time.sleep(0.1)
        # lcd_screen.lcd_display_string(str_pad, 2)

    lcd_screen.clear()
    time.sleep(1)

    display_string_short = display_string[16:]
    lcd_screen.lcd_display_string(display_string_short, 1)
    time.sleep(2.5)
    for x in range(0, (len(display_string) - 16)):
        display_text = display_string_short[x:(x+16)]
        lcd_screen.lcd_display_string(display_text, 1)
        time.sleep(0.1)
