import logging
import os
from pprint import pprint
from datetime import date
import json

from intervalsicu import Intervals

log = logging.getLogger("intervals")

HOME = os.getenv('HOME', '.')
INTERVALS_CONFIG = os.getenv('INTERVALS_CONFIG', HOME + '/.intervals.json')

class IntervalsConfig:
    """This class takes care of the Intervals config file"""

    config = {}
    config_file = ""

    def __init__(self, config_file):
        self.config_file = config_file
        self.read()

    def read(self):
        """reads config file"""
        try:
            with open(self.config_file, encoding="utf8") as configfile:
                self.config = json.load(configfile)
        except (ValueError, FileNotFoundError):
            log.error("Can't read config file %s", self.config_file)
            self.config = {}

    def write(self):
        """writes config file"""
        with open(self.config_file, "w", encoding="utf8") as configfile:
            json.dump(self.config, configfile, indent=4, sort_keys=True)

class IntervalsSync:
    """Main Intervals class"""

    def __init__(self) -> None:
        app_config = IntervalsConfig(INTERVALS_CONFIG)
        self.config = app_config.config
        self.client = Intervals(self.config.get("athlete_id"), self.config.get("api_key"), strict=False)

    def wellness(self, data):
        for item in data:
            if item['type'] == 'weight' and item['fat_ratio'] != 0:
                start = item['date_time'].date()

                icu_wellness = self.client.wellness(start)

                icu_wellness.fields.append('MuscleMass')
                icu_wellness.fields.append('Water')
                icu_wellness.fields.append('BoneMass')

                icu_wellness['bodyFat'] = item['fat_ratio']
                icu_wellness['MuscleMass'] = item['muscle_mass']
                icu_wellness['Water'] = item['percent_hydration']
                icu_wellness['BoneMass'] = item['bone_mass']
                icu_wellness = self.client.wellness_put(icu_wellness)
                log.info(
                    f"Intervals.icu {start}: fat: {item['fat_ratio']:2}%, mm: {item['muscle_mass']:2}kg"
                )
