import i2c_lcd_driver


if __name__ == '__main__':
    lcd_screen = i2c_lcd_driver.lcd()

    lcd_screen.lcd_display_string('Hello, world!', 1)
