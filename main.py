import base
import modules
import engine
import tcod

base.root_console.default_fg = base.cols["outer_fg"]
base.root_console.default_bg = base.cols["outer_bg"]
base.root_console.clear()
base.root_console.draw_frame(1, 1, base.SCREEN_WIDTH-2, base.SCREEN_HEIGHT-2,
                             "ilomusi")
for x, y in [(0, 0), (0, base.SCREEN_HEIGHT-1), (base.SCREEN_WIDTH-1, 0), (base.SCREEN_WIDTH-1, base.SCREEN_HEIGHT-1)]:
    tcod.console_put_char(base.root_console, x, y,
                          "O", tcod.BKGND_NONE)

while True:
    engine.eng.update()
    engine.eng.render()
    tcod.console_flush()
