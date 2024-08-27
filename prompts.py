import questionary
import re

RESOLUTIONS = ['144p', '240p', '360p', '480p', '720p', '1080p']
AUDIO_BITRATES = ['128kbps', '160kbps', '384kbps', '512kbps']

def select_bounds(value, choices):
    lower_bound = questionary.select(
            f"select lower bound: {value}",
            choices=choices).ask() 

    lower_bound_val = remove_units(lower_bound)
    choices = list(filter(lambda x: remove_units(x) >= lower_bound_val, choices))

    upper_bound = questionary.select(
            f"select upper bound {value}",
            choices=choices).ask() 

    return remove_units(lower_bound), remove_units(upper_bound)

def remove_units(s):
    return int(re.sub(r'\D', '', s))
