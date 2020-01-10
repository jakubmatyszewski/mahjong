import cv2
import pyautogui
import mss
import numpy as np

pyautogui.FAILSAFE = True


class Mahjong:
    def __init__(self):
        threshold = 0.2  # Acceptable detection error
        self.min_th, self.max_th = (1-threshold, 1+threshold)
        self.img_path = 'mahjong.png'
        self.pattern_path = 'pattern.png'
        self.rec_ratio, self.h_ratio, self.i_w, self.i_h = self.get_ratios()

    def get_ratios(self):
        """Helper function to understand a tile shape.
        Unfortunately, resizing game window can change tile shape,
        thus different approach have to be considered."""

        img_rgb = cv2.imread(self.img_path, 0)
        i_w, i_h = img_rgb.shape[::-1]
        template = cv2.imread(self.pattern_path, 0)
        t_w, t_h = template.shape[::-1]
        rec_ratio = t_w/t_h  # Expected tile ratio
        h_ratio = t_h/i_h  # Expected tile-to-board height ratio
        return rec_ratio, h_ratio, i_w, i_h

    def grab_screen(self, sct):
        """Capture a screen image."""
        try:
            img = np.array(sct.grab(self.monitor))
        except NameError:
            return "Initiate mss first."
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def clickable(self, sct, tile):
        """Check whether tile is clickable."""
        x, y, w, h = tile

        img = self.grab_screen(sct)
        pre_click = img[y:y+h, x:x+w]

        pyautogui.click(x=(x+w/2), y=(y+h/2))

        img = self.grab_screen(sct)
        post_click = img[y:y+h, x:x+w]

        difference = cv2.subtract(pre_click, post_click)
        b, g, r = cv2.split(difference)
        if (cv2.countNonZero(b) == 0 and
            cv2.countNonZero(g) == 0 and
                cv2.countNonZero(r) == 0):
            return False
        else:
            return tile

    def loc_tiles(self, screen):
        self.tiles = []
        img_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        binary = cv2.bitwise_not(img_gray)
        (contours, _) = cv2.findContours(binary,
                                         cv2.RETR_TREE,
                                         cv2.CHAIN_APPROX_NONE)

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if (w/h > (self.rec_ratio * self.min_th) and
                w/h < (self.rec_ratio * self.max_th) and
                h/self.i_h > (self.h_ratio * self.min_th) and
                    h/self.i_h < (self.h_ratio * self.max_th)):
                self.tiles.append((x, y, h, w))
        print('%d tiles detected.' % len(self.tiles))
        return self.tiles

    def loc_siblings(self, sct, tile, clickables=[]):
        """Finds matching tiles."""
        x, y, h, w = tile
        screen = self.grab_screen(sct)
        look_for = screen[y:y+h, x:x+w]
        result = cv2.matchTemplate(screen, look_for, cv2.TM_CCOEFF_NORMED)
        pattern_threshold = 0.8
        loc = np.where(result >= pattern_threshold)
        sibling = zip(*loc[::-1])
        last_pressed = [0, 0]

        if loc[::-1][0].size == 1:
            # Found only 1 tile of this type.
            return (*list(sibling)[0], h, w)  # TD: Handle unique tiles.

        target = []
        for pt in sibling:
            pt_x = pt[0] + w/2  # Center of tile
            pt_y = pt[1] + h/2  # Center of tile

            if (abs(last_pressed[0] - pt[0]) < 20 and
                    abs(last_pressed[1] - pt[1]) < 20):
                pass
            else:
                for ctile in clickables:
                    cx, cy, ch, cw = ctile
                    if (cx < pt_x < cx+cw and
                            cy < pt_y < cy+ch):
                        clickables.pop(clickables.index(ctile))
                        target.append((pt_x, pt_y))
                        last_pressed = pt

        if len(target) > 1:  # Click only if clickable pair is detected.
            for pew in target:
                pyautogui.click(*pew)

    def solve(self):
        with mss.mss() as sct:
            # Part of the screen to capture
            self.monitor = {"top": 0, "left": 0, "width": 960, "height": 1080}

            while "Screen capturing":
                self.img = self.grab_screen(sct)
                tiles = self.loc_tiles(self.img)
                tiles_count = len(tiles)
                clickable_tiles = []

                for i, tile in enumerate(tiles):
                    clicked = self.clickable(sct, tile)
                    if clicked is not False:
                        clickable_tiles.append(tile)

                # Unclick last clickable tile.
                self.clickable(sct, clickable_tiles[-1])

                img = self.grab_screen(sct)
                check_tiles = self.loc_tiles(img)
                if len(check_tiles) == len(tiles):
                    print('{} clickable tiles.'.format(len(clickable_tiles)))
                    for tile in clickable_tiles:
                        output = self.loc_siblings(sct, tile, clickable_tiles)
                else:
                    pass

                if cv2.waitKey(25) & 0xFF == ord("q"):
                    cv2.destroyAllWindows()
                    break


if __name__ == "__main__":
    Mahjong().solve()
