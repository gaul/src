#!/usr/bin/python3

# TODO: always return json?
# TODO: earthquakes
# TODO: make functions async: https://requests.readthedocs.io/en/v0.8.3/user/advanced/#asynchronous-requests
# TODO: need Japanese font
# TODO: Wanikani integration

import datetime
import os
import logging
import pytz
import requests
import sys
import time
from typing import Any, Optional, Tuple, cast
from PIL import Image, ImageDraw, ImageFont

OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]

def get_weather(city_name: str) -> Tuple[float, str]:
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(city_name, OPENWEATHER_API_KEY)
    resp = requests.get(url)
    assert resp.status_code == 200
    return resp.json()

def get_tokyo_infections() -> Any:
    url = "https://raw.githubusercontent.com/tokyo-metropolitan-gov/covid19/development/data/daily_positive_detail.json"
    resp = requests.get(url)
    assert resp.status_code == 200
    return resp.json()

def get_infections(prefecture_name: str) -> Optional[int]:
    resp = requests.get("https://covid19-japan-web-api.now.sh/api/v1/statistics")
    assert resp.status_code == 200
    for prefecture in resp.json():
        if prefecture["name_en"] == prefecture_name:
            return cast(int, prefecture["total_count"])
    return None

def get_all_infections() -> Tuple[str, int]:
    date = None
    last = None
    current = None
    resp = requests.get("https://covid19-japan-web-api.now.sh/api/v1/total?history=true")
    assert resp.status_code == 200
    for row in resp.json():
        last = current
        current = row["positive"]
        date = row["date"]
    return cast(str, date), cast(int, current - last)

def draw_image() -> Image:
    time_fmt = "%I:%M %p %Z"
    tokyo_time = datetime.datetime.now(pytz.timezone("Asia/Tokyo")).strftime(time_fmt)
    los_angeles_time = datetime.datetime.now(pytz.timezone("America/Los_Angeles")).strftime(time_fmt)
    phoenix_time = datetime.datetime.now(pytz.timezone("America/Phoenix")).strftime(time_fmt)

    output = get_weather("Tokyo")
    tokyo_temperature = output["main"]["temp"] - 273.15
    tokyo_weather = output["weather"][0]["description"]

    tokyo_infections = get_tokyo_infections()
    tokyo_infections_yesterday = tokyo_infections["data"][-1]["count"]
    tokyo_infections_week_ago = tokyo_infections["data"][-8]["count"]

    japan_date, japan_infections = get_all_infections()

    image = Image.new("1", (880, 528), 255)
    draw = ImageDraw.Draw(image)
    font_big = ImageFont.truetype("DroidSans.ttf", 144)
    font = ImageFont.truetype("DroidSans.ttf", 60)
    font_small = ImageFont.truetype("DroidSans.ttf", 24)

    draw.text((10, 10), tokyo_time, font = font_big)
    draw.text((10, 160), los_angeles_time, font = font)
    draw.text((450, 160), phoenix_time, font = font)
    draw.text((10, 240), "{}°C {}".format(int(tokyo_temperature), tokyo_weather), font = font)
    draw.text((10, 320), "{:,} Japan new infections".format(japan_infections), font = font)
    draw.text((10, 400), "{:,} Tokyo, {:+,} w/w".format(tokyo_infections_yesterday, tokyo_infections_yesterday - tokyo_infections_week_ago), font = font)
    draw.text((10, 480), "fetch dates: {}, {}".format(tokyo_infections["data"][-1]["diagnosed_date"], japan_date), font = font_small)

    return image

# TODO: offline mode with fake data
def main() -> None:
    if len(sys.argv) == 2 and sys.argv[1] == "--panel":
        from waveshare_epd import epd7in5b_HD
        epd = epd7in5b_HD.EPD()
        epd.init()
        image_blank = Image.new("1", (880, 528), 255)
        draw_blank = ImageDraw.Draw(image_blank)
        while True:
            epd.Clear()
            try:
                image = draw_image()
                epd.display(epd.getbuffer(image))

                # TODO: what if we draw a red image then don't overwrite it?
                # TODO: better to just use write_bytes2?
                #epd.display(epd.getbuffer(image), epd.getbuffer(image))
                #epd.display(epd.getbuffer(image_blank), epd.getbuffer(image))
            except requests.exceptions.ConnectionError as e:
                logging.error(e)

            # sleep until next 15 minute increment
            time.sleep((15 * 60) - (time.time() % (15 * 60)))
        # TODO: deinitialize on SIGINT?
    else:
        image = draw_image()
        image.save("1.bmp", "BMP")

if __name__ == "__main__":
    main()
