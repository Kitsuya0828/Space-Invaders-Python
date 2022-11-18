# Space Invaders Python


https://user-images.githubusercontent.com/60843722/202617572-89b5d90c-09b9-4f69-93a4-50efb591eb2c.mp4


## Development Environment
* MacBook Pro (2021, Apple M1 Pro)
* Python 3.9.15

## Usage
```zsh
python main.py
```
By using `--help` or `-h` option, you can get a useful message about the game settings.

```zsh
% python main.py --help
usage: main.py [-h] [--diff DIFF] [--lives LIVES]

optional arguments:
  -h, --help     show this help message and exit
  --diff DIFF    the game difficulty (default=easy, easy | medium | hard)
  --lives LIVES  the initial number of lives (default=3)
```

You can run the program with the following commands:

```zsh
python main.py
```

---

## Raspberry Pi Implementation

![IMG_8485](https://user-images.githubusercontent.com/60843722/202617798-607b696c-6665-46c3-92a4-176ee3fb63ca.jpg)


You can also run this program on the [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi).

[WiringPi](https://github.com/WiringPi/WiringPi-Python) is an implementation of most of the Arduino Wiring functions for the Raspberry Pi. The library is packaged on PyPI and can be installed with pip:
```
pip install wiringpi
```

Before running the program, execute the following command on the LXTerminal.

```zsh
gpio export 5 out
gpio export 6 out
gpio export 13 out
gpio export 19 in
gpio export 21 in
gpio export 26 in
```

Now, you can run the program with the following commands:

```zsh
python raspi_main.py
```
