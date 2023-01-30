# FEZ Randomizer

## Installation

Download and unzip the release zip file and copy it to your `Mods` folder (see
[the HAT Github page](https://github.com/Krzyhau/HAT) for more information). It is not possible to use this mod zipped,
because the config file used to store the randomization needs to be in the same folder as the mod in order to work.

## Building the Mod

- Copy all the necessary dependencies into `Dependencies`
- Press build
- ???
- Profit

## Using the Randomizer

In the project root directory, run `python3 src/randomizer.py`. Copy the generated output `config.txt` into the same
folder as the mod (e.g. `Mods/Randomizer`).

## Current Limitations and Future Work

Right now this only randomizes entrances in Villageville, so it's mostly a tech demo. Future work will involve mapping
the whole game, as well as randomizing lesser gates and chests, as well as handling key logic.