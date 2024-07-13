
# DoScreen

*DO* specific (key or mouse) clicks and/or simulate typing a string when some given picture is visible on *SCREEN*
## Installation

Install with pip

```bash
  pip install -r requirements.txt
```

### Linux:
On Linux you also need to install python3-tk:

Example for Ubuntu:
```bash
 sudo apt-get install python3-tk
 ```
## Usage

#### Windows:
`python doscreen.py`

#### Linux:
`python3 doscreen.py`

#### Keywords:
`threshold` --> percentage of how similar the given picture must be to the image on the screen to trigger the assigned actions

`click` --> normal left click

`dbl_click` --> right click

`r_click` --> double click

`key` --> emulate pressing a key

`type` --> emulate typing a string


#### Additions:
 - You can use the `do_sth.py` to test different actions
 - You can use the `recog_pics.py` to test the picture recognizion
 - You can use the `recog_pics.py` or the `doscreen.py` to test the picture recognizion and value for the `threshold` parameter
 - You can use the given example pics for all kinds of testing purposes as well


## Screenshots

![image](https://github.com/user-attachments/assets/c6b1f160-38aa-4d95-99e4-4553c3a66ad3)


