mahjong solitaire solver

---

Script that solves mahjong solitaire (`https://www.kurnik.pl/mahjong/`).
Before running the script make sure a game window is visible on your screen.

v0.2:
- look for pair only if tiles are clickable
- improve timing and accuracy by skipping tiles that have no pairs
- fix looping over already collected tiles (game-state tracking issue)
- prevent clicking same tile twice

v0.1:
- localize tiles on the board
- categorize active (clickable) tiles
- find pattern pairs
- click to match pairs

Todo:

- [x] Improve active tiles detection
- [ ] Improve pattern detection (some tiles are unique - golden and black tiles)
- [x] Fix file structure; `.ipynb` -> `.py`
- [ ] Improve game-state tracking