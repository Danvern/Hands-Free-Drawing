from typing import Tuple

from talon import Context, Module, canvas, cron, ctrl, screen, ui
from talon.skia import Shader, Color, Paint, Rect

class PixelEditor:
    def __init__(self, width: float, height: float):
        self.enabled = False
        self.canvas = None
        self.bounding_rect =  Rect(0, 0, width, height)
        self.job = None
        self.last_pos = None
        # self.width = width
        # self.height = height
        self.cell_size = 10

    def enable(self):
        if self.enabled:
            return
        self.enabled = True
        self.last_pos = None
        screen = ui.screens()[0]
        self.canvas = canvas.Canvas(0, 0, screen.width, screen.height)
        if self.bounding_rect is None:
            self.bounding_rect = screen.rect.copy()
        # self.check_mouse()
        # self.canvas.register('mousemove', self.on_mouse)
        self.canvas.register('draw', self.draw_canvas)
        self.canvas.freeze()
        # self.job = cron.interval('16ms', self.check_mouse)

    def disable(self):
        if not self.enabled:
            return
        # cron.cancel(self.job)
        self.enabled = False
        self.canvas.close()
        self.canvas = None

    def toggle(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def adjust_grid_spacing(self, spacing: int):
        self.cell_size = spacing
        self.canvas.freeze()
            
    def adjust_grid_size(self, width_adjust: int, height_adjust: int):
        print('request width:', width_adjust, 'request height:', height_adjust)
        if(self.bounding_rect.width + width_adjust > 0):
            self.bounding_rect.width += width_adjust
        else:
            self.bounding_rect.width = 1
        if(self.bounding_rect.height + height_adjust > 0):
            self.bounding_rect.height += height_adjust
        else:
            self.bounding_rect.height = 1
        # self.canvas.height = self.height
        # print('canvas width:', self.canvas.width, 'canvas height:', self.canvas.height)
        print('grid width:', self.bounding_rect.width, 'grid height:', self.bounding_rect.height)
        self.canvas.freeze()

    def adjust_grid_position(self, x_adjust: int, y_adjust: int):
        # print('request width:', width_adjust, 'request height:', height_adjust)
        if(self.bounding_rect.x + x_adjust > self.canvas.rect.width):
            self.bounding_rect.x = self.canvas.rect.width - 1
        elif(self.bounding_rect.x + x_adjust > 0):
            self.bounding_rect.x += x_adjust
        else:
            self.bounding_rect.x = 0
        if(self.bounding_rect.y + y_adjust > self.canvas.rect.height):
            self.bounding_rect.y = self.canvas.rect.height - 1
        elif(self.bounding_rect.y + y_adjust > 0):
            self.bounding_rect.y += y_adjust
        else:
            self.bounding_rect.y = 0
        # self.canvas.height = self.height
        # print('canvas width:', self.canvas.width, 'canvas height:', self.canvas.height)
        print('grid width:', self.bounding_rect.width, 'grid height:', self.bounding_rect.height)
        self.canvas.freeze()

    def adjust_grid_position_to_mouse(self):
        self.bounding_rect.x, self.bounding_rect.y = ctrl.mouse_pos()
        self.canvas.freeze()

    def cell_coordinate(self, character: str, number: int) -> Tuple[int, int]:
        x = number
        # turn the character into a number, 97 is 'a'
        y = ord(character.lower()) - 97
        # multiply by cell size and add half as an offset
        x = x * self.cell_size + self.cell_size * 0.5 + self.bounding_rect.x
        y = y * self.cell_size + self.cell_size * 0.5 + self.bounding_rect.y
        return x, y
        
    def draw_canvas(self, canvas):
        paint = canvas.paint
        paint.color = '0000001f'
        rect = self.bounding_rect

        i_range = lambda start, stop, step: range(int(start), int(stop), int(step))
        paint.antialias = False
        # adan of that value sod the left the line renders
        offset = 1
        for x in i_range(rect.left + offset, rect.right, self.cell_size):
            canvas.draw_line(x, rect.top, x, rect.bot)
        for y in i_range(rect.top, rect.bot, self.cell_size):
            canvas.draw_line(rect.left, y, rect.right, y)        
        # for off, color in ((0, '55ffaa20'), (1, '000000ff')):
            # paint.color = color
            # draw axis lines
            # cx, cy = rect.center
            # cxo = cx + off
            # cyo = cy + off

            # draw ticks
            # for tick_dist, tick_length in ((SMALL_DIST, SMALL_LENGTH),
                                           # (LARGE_DIST, LARGE_LENGTH)):
                # half = tick_length // 2
                # ticks to the left
                # for x in irange(rect.left + off, cx - tick_dist + 1, tick_dist):
                    # canvas.draw_line(x, cy - half, x, cy + half)
                # ticks to the right
                # for x in irange(cxo + tick_dist - 1, rect.right + 1, tick_dist):
                    # canvas.draw_line(x, cy - half, x, cy + half)
                # ticks above
                # for y in irange(rect.top + off + 1, cy - tick_dist + 1, tick_dist):
                    # canvas.draw_line(cx - half, y, cx + half, y)
                # ticks below
                # for y in irange(cyo + tick_dist, rect.bot + 1, tick_dist):
                    # canvas.draw_line(cx - half, y, cx + half, y)

    # def on_mouse(self, event):
        # self.check_mouse()

    # def check_mouse(self):
        # pos = ctrl.mouse_pos()
        # if pos != self.last_pos:
            # x, y = pos
            # self.canvas.move(x, y)
            # self.last_pos = pos
            
pixel_editor = PixelEditor(500, 500)
pixel_editor.enable()

modo = Module()
modo.list('directional', desc='directions for expansion')

def interpret_direction(distance: int, direction: str) -> Tuple[int, int]:
    if direction == 'left':
        return -distance, 0
    elif direction == 'right':
        return distance, 0
    elif direction == 'up':
        return 0, -distance
    elif direction == 'down':
        return 0, distance
    raise ValueError(f"not a great direction: {direction}")

@modo.action_class
class Actions:
    def pixel_editor_on():
        """Turn on the pixel editor"""
        pixel_editor.enable()

    def pixel_editor_off():
        """Turn off the pixel editor"""
        pixel_editor.disable()

    def pixel_editor_toggle():
        """Turn on the pixel editor, or off if it is already on"""
        pixel_editor.toggle()

    def jump_to_grid(character: str, number: int):
        """Moves the indicate position"""
        x, y = pixel_editor.cell_coordinate(character, number)
        ctrl.mouse_move(x, y)
    
    def editor_adjust_position(number: int, direction: str):
        '''move the grid overlay'''
        x, y = interpret_direction(number, direction)
        pixel_editor.adjust_grid_position(x, y)
        
    def editor_adjust_position_2d(number: int, direction: str, number2: int, direction2: str):
        '''move the grid overlay'''
        x, y = interpret_direction(number, direction)
        x2, y2 = interpret_direction(number2, direction2)
        pixel_editor.adjust_grid_position(x + x2, y + y2)
        
    def editor_adjust_size(number: int, direction: str):
        '''move the grid overlay'''
        x, y = interpret_direction(number, direction)
        pixel_editor.adjust_grid_size(x, y)
        
    def editor_adjust_size_2d(number: int, direction: str, number2: int, direction2: str):
        '''move the grid overlay'''
        x, y = interpret_direction(number, direction)
        x2, y2 = interpret_direction(number2, direction2)
        pixel_editor.adjust_grid_size(x + x2, y + y2)
        
    def editor_adjust_spacing(number: int):
        '''adjust the cell with'''
        pixel_editor.adjust_grid_spacing(number)
        
    def editor_adjust_position_cursor():
        '''moved to cursor'''
        pixel_editor.adjust_grid_position_to_mouse()

ctx = Context()
ctx.lists['user.directional'] = [
    'up', 'down', 'right', 'left', 
]