# Tetris bot solver

A bot driven by AI that plays Tetris on a real Android phone. It uses screen analysis with computer vision, a planning search to choose actions, and ADB control commands.

## What it does

The bot runs over and over:

1. It takes a phone screenshot with ADB.  
2. It finds the Tetris playfield using computer vision.  
3. It reads the active shape and the “next” queue.  
4. It rebuilds the match as a 10×20 grid.  
5. It uses a search routine to rate possible moves.  
6. It decides how to rotate and shift left or right.  
7. It sends button presses to the Android app via ADB.  
8. It checks that the detected situation still matches before it acts.  
9. Then it repeats the same steps for the next shape.

## How the AI thinks

For each candidate placement, the AI scores outcomes using things like:

- cleared lines  
- total column height  
- empty gaps under blocks  
- uneven surface profile  

It also looks ahead at upcoming shapes, not only the current one.  
The current version searches across several upcoming pieces to pick stronger actions.

## Computer vision

OpenCV is used to inspect screenshots from the Android device.

It detects:

- the filled or empty cells on the Tetris board  
- the falling piece right now  
- the upcoming “next” pieces  
- the piece placement on the grid  

The playfield is turned into a standard **10 × 20 Tetris grid** for the AI.

## Android automation

The phone control runs through **Android Debug Bridge (ADB)**.

The bot can do:

- move left  
- move right  
- rotate  
- hard drop  

It also rechecks the seen game layout before running its plan, so it avoids acting on outdated readings.

## Layout

```text
┌──────────────────────┐
│    Android Tetris    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    ADB Screenshot    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Computer Vision    │
│       OpenCV         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Game State        │
│     10 × 20 Board    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     Search AI        │
│ Board Rating +       │
│ Lookahead Search     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     Move Planner     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      ADB Input       │
└──────────┬───────────┘
           │
           ▼
        Repeat
```
