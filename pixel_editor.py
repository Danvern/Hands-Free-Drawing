from typing import Tuple

from talon import Context, Module, canvas, cron, ctrl, screen, ui
from talon.skia import Shader, Color, Paint, Rect

class PixelEditor:
    def __init__(self, width: float, height: float):
        self.enabled = False
        self.canvas = None
        screen = ui.screens()[0]
        self.max_rect = screen.rect.copy()
        self.grids = [self.FlexibleGrid(width, height, self.max_rect)]
        self.active_grid = 0

    def enable(self):
        if self.enabled:
            return
        self.enabled = True
        screen = ui.screens()[0]
        self.canvas = canvas.Canvas(0, 0, screen.width, screen.height)
        self.canvas.register('draw', self.draw_canvas)
        self.canvas.freeze()

    def disable(self):
        if not self.enabled:
            return
        self.enabled = False
        self.canvas.close()
        self.canvas = None

    def toggle(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()
            
    class FlexibleGrid:
        def __init__(self, width: float, height: float, maximum_bounds: Rect):
            self.bounding_rect =  Rect(0, 0, width, height)
            self.cell_size = 10
            self.max_rect = maximum_bounds
            screen = ui.screens()[0]
            if self.max_rect is None:
                self.max_rect = screen.rect.copy()
        
        def set_grid_spacing(self, spacing: int):
            self.cell_size = spacing if spacing > 0 else 1 
                
        def set_grid_size(self, x: int, y: int):
            if(x > self.max_rect.width):
                self.bounding_rect.width = self.max_rect.width
            elif(x > 0):
                self.bounding_rect.width = x
            else:
                self.bounding_rect.width = 1
            if(y > self.max_rect.height):
                self.bounding_rect.height = self.max_rect.height
            elif(y > 0):
                self.bounding_rect.height = y
            else:
                self.bounding_rect.height = 1
                
        def adjust_grid_size(self, width_adjust: int, height_adjust: int):
            self.set_grid_position(self.bounding_rect.width + width_adjust, self.bounding_rect.height + height_adjust)

        def set_grid_position(self, x: int, y: int):
            if(x > self.max_rect.width):
                self.bounding_rect.x = self.max_rect.width - 1
            elif(x > 0):
                self.bounding_rect.x = x
            else:
                self.bounding_rect.x = 0
            if(y > self.max_rect.height):
                self.bounding_rect.y = self.max_rect.height - 1
            elif(y > 0):
                self.bounding_rect.y = y
            else:
                self.bounding_rect.y = 0

        def adjust_grid_position(self, x_adjust: int, y_adjust: int):
            self.set_grid_position(self.bounding_rect.x + x_adjust, self.bounding_rect.y + y_adjust)

        def adjust_grid_position_to_mouse(self):
            self.set_grid_position(ctrl.mouse_pos())

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

    # draw the currently active grid
    def draw_canvas(self, canvas):
        self.grids[self.active_grid].draw_canvas(canvas)
    
    # adjust the cell size of the specified grid in both directions equally
    def set_grid_spacing(self, spacing: int, identifier = 0):
        self.grids[identifier].set_grid_spacing(spacing)
        self.canvas.freeze()
            
    # change the size of the specified grid
    def adjust_grid_size(self, width_adjust: int, height_adjust: int, identifier = 0):
        self.grids[identifier].adjust_grid_size(width_adjust, height_adjust)
        self.canvas.freeze()

    # move the specified grid by the specified amount 
    def adjust_grid_position(self, x_adjust: int, y_adjust: int, identifier = 0):
        self.grids[identifier].adjust_grid_position(x_adjust, y_adjust)
        self.canvas.freeze()

    # move the specified grid to the mouse cursor 
    def adjust_grid_position_to_mouse(self, identifier = 0):
        self.grids[identifier].adjust_grid_position_to_mouse()
        self.canvas.freeze()
            
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
        pixel_editor.set_grid_spacing(number)
        
    def editor_adjust_position_cursor():
        '''moved to cursor'''
        pixel_editor.adjust_grid_position_to_mouse()

ctx = Context()
ctx.lists['user.directional'] = [
    'up', 'down', 'right', 'left', 
]