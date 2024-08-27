import questionary
import sys
import prompts
from rich import print

ub, lb = prompts.select_bounds("resolution", prompts.RESOLUTIONS)
print(f"Lower Bound: {ub} Upper Bound: {lb}")
ub, lb = prompts.select_bounds("audio bit rate", prompts.AUDIO_BITRATES)
print(f"Lower Bound: {ub} Upper Bound: {lb}")
