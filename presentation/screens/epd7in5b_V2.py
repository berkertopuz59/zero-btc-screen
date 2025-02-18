import os
from PIL import Image, ImageDraw, ImageFont
try:
    from waveshare_epd import epd7in5b_V2
except ImportError:
    pass
from data.plot import Plot
from presentation.observer import Observer

# Updated screen dimensions for 7.5-inch display
EPD_WIDTH = 800
EPD_HEIGHT = 480

# Fonts
FONT_SMALL = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'Roses.ttf'), 24)  # Adjusted font size
FONT_LARGE = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), os.pardir, 'PixelSplitter-Bold.ttf'), 64)  # Adjusted font size

class Epd7in5bV2(Observer):

    def __init__(self, observable, mode):
        super().__init__(observable=observable)
        self.epd = epd7in5b_V2.EPD()

        self.epd.init()
        self.image_black = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)  # Black image
        self.image_red = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)    # Red image
        self.draw_black = ImageDraw.Draw(self.image_black)
        self.draw_red = ImageDraw.Draw(self.image_red)
        self.mode = mode

    def form_image(self, prices):
        # Clear the screen with white
        self.draw_black.rectangle((0, 0, EPD_WIDTH, EPD_HEIGHT), fill="white")
        self.draw_red.rectangle((0, 0, EPD_WIDTH, EPD_HEIGHT), fill="white")

        # Draw the chart
        if self.mode == "candle":
            Plot.candle(prices, size=(EPD_WIDTH - 120, EPD_HEIGHT - 80), position=(100, 40), draw=self.draw_black)
        else:
            last_prices = [x[3] for x in prices]
            Plot.line(last_prices, size=(EPD_WIDTH - 120, EPD_HEIGHT - 80), position=(100, 40), draw=self.draw_black)

        # Draw Y-axis labels
        flatten_prices = [item for sublist in prices for item in sublist]
        Plot.y_axis_labels(flatten_prices, FONT_SMALL, (20, 40), (80, EPD_HEIGHT - 80), draw=self.draw_black)

        # Draw horizontal and vertical lines
        self.draw_black.line([(100, EPD_HEIGHT - 40), (EPD_WIDTH - 20, EPD_HEIGHT - 40)])  # X-axis line
        self.draw_black.line([(100, 40), (100, EPD_HEIGHT - 40)])  # Y-axis line
        self.draw_black.line([(150, EPD_HEIGHT - 30), (150, EPD_HEIGHT - 20)])  # Example tick mark

        # Draw the caption (e.g., latest price)
        Plot.caption(flatten_prices[len(flatten_prices) - 1], EPD_HEIGHT - 30, EPD_WIDTH, FONT_LARGE, self.draw_black)

    def update(self, data):
        self.form_image(data)
        image_black_rotated = self.image_black.rotate(180)
        image_red_rotated = self.image_red.rotate(180)
        self.epd.display(
            self.epd.getbuffer(image_black_rotated),
            self.epd.getbuffer(image_red_rotated)
        )

    def close(self):
        self.epd.Dev_exit()
