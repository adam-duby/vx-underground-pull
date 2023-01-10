'''
Last Update: 1 FEB 2022
Description: Extracts malware from vx-underground
Warning: Running this will install live malware executables.
'''

import re
import requests
import subprocess

from pathlib import Path

BASE_URL = "https://samples.vx-underground.org/samples/Families"
BASE_PATTERN = re.compile(f"{BASE_URL}/([^/'\"]+)/")
EXTRACTION_COMMAND = "7z e -pinfected {}"
SAMPLE_PATH = "./Samples"


def collect_samples(url):
    samples = {}

    samples_pattern = f"{url}([^/'\"]+)\\.7z"
    subdir_pattern = f"{url}[^/'\"]+/"

    index = requests.get(url).text
    for sample in re.finditer(samples_pattern, index):
        samples[sample[1]] = sample[0]

    for subdir in re.finditer(subdir_pattern, index):
        samples.update(collect_samples(subdir[0]))

    return samples


family_index = requests.get(BASE_URL).text
for family in BASE_PATTERN.finditer(family_index):
    print(family[1])

    for sample, url in collect_samples(family[0]).items():
        filename = Path(SAMPLE_PATH) / family[1] / sample
        filename.parent.mkdir(parents=True, exist_ok=True)

        if not filename.exists():
            sample_7z = filename.with_suffix(".7z")
            sample_7z_contents = requests.get(url).content
            with open(filename.with_suffix(".7z"), "wb") as f:
                f.write(sample_7z_contents)
            subprocess.run(
                ["7z", "e", "-pinfected", f"-o{filename.parent}", sample_7z],
                capture_output=True,
            )
            sample_7z.unlink()

            print(f"  {sample}")
