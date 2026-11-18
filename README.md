# Ping Pong: AI vs Player

A simple Ping Pong game built with Python and Pygame, featuring a player-controlled paddle against an AI opponent.

## Features

- Player vs AI gameplay
- AI predicts the ball's movement
- Paddle collision physics
- Ball speed increases during gameplay
- Score system
- First player to reach 5 points wins
- Replay and quit options

## Requirements

- Python 3.x
- Pygame

## Installation

Install the required dependency:

```bash
pip install -r requirements.txt
```

## Run the Game

```bash
python ping_pong.py
```

## Controls

| Key | Action |
|---|---|
| W | Move player paddle up |
| S | Move player paddle down |
| SPACE | Start the game |
| R | Replay after game over |
| Q | Quit after game over |

## Gameplay

The player controls the left paddle using **W** and **S**.

The AI controls the right paddle and predicts where the ball will reach in order to move its paddle toward the predicted position.

The first player to reach **5 points** wins.