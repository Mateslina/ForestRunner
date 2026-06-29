# Forest Runner

The game features an endlessly repeating environment with obstacles, that becomes progressively faster and more difficult over time. During gameplay, the player must avoid these obstacles by jumping or crouching. The main objective is to achieve the highest possible score.

In addition to avoiding obstacles, the player can collect **coins** and various **power-ups**. Collected coins can be used to enhance duration of these power-ups in the shop for future runs.


## Dependencies

- developed in **Python 3.13**
- **pygame** 
- **pytest** 
- **pytest-cov**

All required dependencies are listed in `requirements.txt`.


## Installation

It is recommended to run the project inside a virtual environment.
Pygame doesn't seem to be supported yet in python 3.14 so use older versions.
If you want a fresh save of the game, just delete the app/runner_save.json. I kept it there if anyone wanted to beat my high score :).

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

All commands below are executed **from inside the `src` directory**.

To start the game, run:
```bash
python3 -m main.main
```

To run tests with code coverage:
```bash
pytest --cov=main
```