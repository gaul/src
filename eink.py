#!/usr/bin/python3

# TODO: always return json?
# TODO: earthquakes
# TODO: make functions async: https://requests.readthedocs.io/en/v0.8.3/user/advanced/#asynchronous-requests
# TODO: need Japanese font
# TODO: Wanikani integration
# TODO: humidity
# TODO: pollen

import datetime
import os
import logging
import pytz
import requests
import subprocess
import sys
import time
from typing import Any, List, Optional, Tuple, cast
from PIL import Image, ImageDraw, ImageFont

OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
JAPAN_POPULATION = 126_300_000
# TODO: HTTPS
ALL_VACINATIONS = "http://www.kantei.go.jp/jp/content/vaccination_data5.pdf"
# TODO: set full path for Pi
DROID_FONT_PATH = "DroidSans.ttf"

def get_weather(city_name: str) -> Tuple[float, str]:
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(city_name, OPENWEATHER_API_KEY)
    resp = requests.get(url)
    # TODO: something more precise than AssertionError?
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
    resp = requests.get("https://covid19-japan-web-api.now.sh/api/v1/total?history=true")
    last = 0
    assert resp.status_code == 200
    result = []
    for row in resp.json():
        current = row["positive"]
        result += [(row["date"], current - last)]
        last = current
    return result

def get_all_vacinations(cmd: str) -> List[Tuple[str, int]]:
    output = subprocess.run(cmd, capture_output=True, text=True)
    output.check_returncode()
    result = []
    for line in output.stdout.split("\n"):
        parts = line.split()
        if "2021/" in line and len(parts) >= 7:
            date, weekday, total, pfizer_first, moderna_first, pfizer_second, moderna_second = parts[:7]
        elif "合計" in line and len(parts) >= 6:
            date, total, pfizer_first, moderna_first, pfizer_second, moderna_second = parts[:6]
            weekday = None
        else:
            continue
        total = int(total.replace(",", ""))
        pfizer_first = int(pfizer_first.replace(",", ""))
        pfizer_second = int(pfizer_second.replace(",", ""))
        moderna_first = int(moderna_first.replace(",", ""))
        moderna_second = int(moderna_second.replace(",", ""))
        result += [(date, pfizer_first + moderna_first, pfizer_second + moderna_second)]
    return result

def get_workplace_vacinations(cmd: str) -> List[Tuple[str, int]]:
    output = subprocess.run(cmd, capture_output=True, text=True)
    output.check_returncode()
    result = []
    for line in output.stdout.split("\n"):
        parts = line.split()
        if "2021/" in line and len(parts) >= 7:
            date1, weekday1, date2, weekday2, total, first, second, = parts[:7]
        else:
            continue
        total = int(total.replace(",", ""))
        first = int(first.replace(",", ""))
        second = int(second.replace(",", ""))
        result += [(date1, first, second)]
    return result

def draw_image() -> Image:
    time_fmt = "%I:%M %p"
    time_zone_fmt = "%I:%M %p %Z"
    tokyo_time = datetime.datetime.now(pytz.timezone("Asia/Tokyo")).strftime(time_fmt)
    los_angeles_time = datetime.datetime.now(pytz.timezone("America/Los_Angeles")).strftime(time_zone_fmt)
    phoenix_time = datetime.datetime.now(pytz.timezone("America/Phoenix")).strftime(time_zone_fmt)

    output = get_weather("Tokyo")
    tokyo_temperature = output["main"]["temp"] - 273.15
    tokyo_weather = output["weather"][0]["description"]

    tokyo_infections = get_tokyo_infections()
    tokyo_infections_yesterday = tokyo_infections["data"][-1]["count"]
    tokyo_infections_week_ago = tokyo_infections["data"][-8]["count"]

    japan_infections = get_all_infections()
    japan_infections_yesterday = japan_infections[-1][1]
    japan_infections_week_ago = japan_infections[-8][1]

    try:
        raise Exception()
        # TODO: use single curl command
        japan_healthcare_vaccinations = get_all_vacinations(
                ["bash", "-c", "curl --silent " + ALL_VACINATIONS + " | pdftotext -f 3 -l 3 -layout - -"])
        japan_elderly_vaccinations = get_all_vacinations(
                ["bash", "-c", "curl --silent " + ALL_VACINATIONS + " | pdftotext -f 2 -l 2 -layout - -"])
        japan_workplace_vaccinations = get_workplace_vacinations(
                ["bash", "-c", "curl --silent " + ALL_VACINATIONS + " | pdftotext -f 4 -l 4 -layout - -"])
        duplicate_vaccinations = get_workplace_vacinations(
                ["bash", "-c", "curl --silent " + ALL_VACINATIONS + " | pdftotext -f 5 -l 5 -layout - -"])
        japan_first_vaccinations_total = (
                japan_healthcare_vaccinations[0][1] + japan_elderly_vaccinations[0][1] + japan_workplace_vaccinations[0][1] - duplicate_vaccinations[0][1])
        japan_second_vaccinations_total = (
                japan_healthcare_vaccinations[0][2] + japan_elderly_vaccinations[0][2] + japan_workplace_vaccinations[0][2])
        japan_vaccinations_date = japan_elderly_vaccinations[1][0]
    except:
        japan_healthcare_vaccinations = 0
        japan_elderly_vaccinations = 0
        japan_first_vaccinations_total = 0
        japan_second_vaccinations_total = 0
        japan_vaccinations_date = 0

    image = Image.new("1", (880, 528), 255)
    draw = ImageDraw.Draw(image)
    font_big = ImageFont.truetype(DROID_FONT_PATH, 144)
    font = ImageFont.truetype(DROID_FONT_PATH, 60)
    font_small = ImageFont.truetype(DROID_FONT_PATH, 24)

    draw.text((140, 0), tokyo_time, font = font_big)
    draw.multiline_text((10, 140), """\
{}      {}
{}°C {}
{:,} Tokyo new inf., {:+,} w/w
""".format(
#{:,} Japan new inf., {:+,} w/w
#{:.1f}% 1st vac., {:.1f}% 2nd vac.
    los_angeles_time, phoenix_time,
    int(tokyo_temperature), tokyo_weather,
    #japan_infections_yesterday, japan_infections_yesterday - japan_infections_week_ago,
    tokyo_infections_yesterday, tokyo_infections_yesterday - tokyo_infections_week_ago),
    #japan_first_vaccinations_total / JAPAN_POPULATION * 100.0,
    #japan_second_vaccinations_total / JAPAN_POPULATION * 100.0),
    font = font, spacing = 12)
    draw.text((10, 490), "fetch dates: {}, {}, {}".format(
        tokyo_infections["data"][-1]["diagnosed_date"],
        japan_infections[-1][0],
        japan_vaccinations_date),
        font = font_small)

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
            except (AssertionError, requests.exceptions.ConnectionError, subprocess.CalledProcessError) as e:
                logging.error(e)
                time.sleep((15 * 60) - (time.time() % (15 * 60)))
                continue

            epd.display(epd.getbuffer(image))

            # TODO: what if we draw a red image then don't overwrite it?
            # TODO: better to just use write_bytes2?
            #epd.display(epd.getbuffer(image), epd.getbuffer(image))
            #epd.display(epd.getbuffer(image_blank), epd.getbuffer(image))

            # sleep until next 15 minute increment
            time.sleep((15 * 60) - (time.time() % (15 * 60)))
        # TODO: deinitialize on SIGINT?
    else:
        image = draw_image()
        # TODO: require -o out.bmp
        image.save("1.bmp", "BMP")

if __name__ == "__main__":
    main()
