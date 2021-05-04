from typing import Tuple

from talon import Context, Module, canvas, cron, ctrl, screen, ui, clip
from talon.skia import Shader, Color, Paint, Rect

class PixelEditor:
    def __init__(self, width: float, height: float):
        self.enabled = False
        self.canvas = None
        screen = ui.screens()[0]
        self.max_rect = screen.rect.copy()
        self.grids = []
        # self.grids = [self.FlexibleGrid(width, height, self.max_rect)]
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
        def __init__(self, x: int, y: int, width: float, height: float, maximum_bounds: Rect, /, cell_width = 10, cell_height = 10):
            self.bounding_rect =  Rect(x, y, width, height)
            self.cell_width = cell_width
            self.cell_height = cell_height
            self.max_rect = maximum_bounds
            screen = ui.screens()[0]
            if self.max_rect is None:
                self.max_rect = screen.rect.copy()
        
        """Set the height and width of each grid cell to the specified value."""
        def set_grid_spacing(self, spacing: int):
            spacing = spacing if spacing > 0 else 1 
            self.cell_width = spacing
            self.cell_height = spacing

        """Set the height and width of each grid cell independently to the specified values."""
        def set_grid_spacing_2d(self, width: int, height: int):
            self.cell_width = width if width > 0 else 1
            self.cell_height = height if height > 0 else 1
                
        """Adjust the height and width of the grid cells relative to their width, making them square."""
        def adjust_grid_spacing(self, spacing_adjust: int):
            self.set_grid_spacing(self.cell_width + spacing_adjust)

        """Adjust the height and width of the grid cells independently by the specified values."""
        def adjust_grid_spacing_2d(self, spacing_adjust_x: int, spacing_adjust_y: int):
            self.set_grid_spacing_2d(self.cell_width + spacing_adjust_x, self.cell_height + spacing_adjust_y)
                
        """Set the height and width of the grid to the specified values."""
        def set_grid_size(self, x: int, y: int):
            if(x > self.max_rect.width - self.bounding_rect.x):
                self.bounding_rect.width = self.max_rect.width - self.bounding_rect.x
            elif(x > 0):
                self.bounding_rect.width = x
            else:
                self.bounding_rect.width = 1
            if(y > self.max_rect.height - self.bounding_rect.y):
                self.bounding_rect.height = self.max_rect.height - self.bounding_rect.y
            elif(y > 0):
                self.bounding_rect.height = y
            else:
                self.bounding_rect.height = 1
                
        """Adjust the height and width of the grid by the specified values."""
        def adjust_grid_size(self, width_adjust: int, height_adjust: int):
            self.set_grid_size(self.bounding_rect.width + width_adjust, self.bounding_rect.height + height_adjust)

        """Resize the grid from its origin to the current position of the cursor."""
        def adjust_grid_size_to_mouse(self):
            r = self.bounding_rect
            m = ctrl.mouse_pos()
            x = m[0] - r.x
            y = m[1] - r.y
            # If an axis is negative move the grid by the amount so an anchor is maintained
            self.adjust_grid_position(x if x < 0 else 0, y if y < 0 else 0)
            self.set_grid_size(abs(x), abs(y))

        """Set the upper left corner of the grid to the specified point."""
        def set_grid_position(self, x: int, y: int):
            print(self.get_info())
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
            print(self.get_info())

        """Move the grid by the specified values."""
        def adjust_grid_position(self, x_adjust: int, y_adjust: int):
            self.set_grid_position(self.bounding_rect.x + x_adjust, self.bounding_rect.y + y_adjust)

        """Set the upper left corner of the grid to the mouse cursor position."""
        def adjust_grid_position_to_mouse(self):
            self.set_grid_position(*ctrl.mouse_pos())
            
        """Return integer coordinates from a character - integer combination."""
        def cell_coordinate(self, character: str, number: int) -> Tuple[int, int]:
            x = number
            # turn the character into a number, 97 is 'a'
            y = ord(character.lower()) - 97
            # multiply by cell size and add half as an offset
            x = x * self.cell_size + self.cell_size * 0.5 + self.bounding_rect.x
            y = y * self.cell_size + self.cell_size * 0.5 + self.bounding_rect.y
            return x, y

        """Draw the graphical representation of the grid."""        
        def draw_canvas(self, canvas):
            paint = canvas.paint
            paint.color = '000055ff'
            rect = self.bounding_rect

            i_range = lambda start, stop, step: range(int(start), int(stop), int(step))
            paint.antialias = False
            # to make sure the left line renders (probably not necessary)
            offset = 1
            for x in i_range(rect.left + offset, rect.right, self.cell_width):
                canvas.draw_line(x, rect.top, x, rect.bot)
            for y in i_range(rect.top, rect.bot, self.cell_height):
                canvas.draw_line(rect.left, y, rect.right, y)        

        """Return a string of structural information."""        
        def get_info(self) -> str:
            r = self.bounding_rect
            return f"X: {r.x}, Y: {r.y}, Width: {r.width}, Height: {r.height}, Cell Width: {self.cell_width}, Cell Height: {self.cell_height}"
            
        """Return a command formatted as a string to generate this grid."""
        def get_preset(self) -> str:
            r = self.bounding_rect
            return f"add_grid({r.x}, {r.y}, {r.width}, {r.height}, {self.cell_width}, {self.cell_height})"

    """Draw the currently active grid."""
    def draw_canvas(self, canvas):
        if len(self.grids) > 0:
            self.grids[self.active_grid].draw_canvas(canvas)
    
    """Set the cell size of the specified grid in both directions equally."""
    def set_grid_spacing(self, spacing: int, identifier = 0):
        self.grids[identifier].set_grid_spacing(spacing)
        self.canvas.freeze()
            
    """Set the cell size of the specified grid in both directions equally."""
    def set_grid_spacing_2d(self, spacing_x: int, spacing_y: int, identifier = 0):
        self.grids[identifier].set_grid_spacing_2d(spacing_x, spacing_y)
        self.canvas.freeze()
            
    """Adjust the cell size of the specified grid in both directions equally."""
    def adjust_grid_spacing(self, spacing: int, identifier = 0):
        self.grids[identifier].adjust_grid_spacing(spacing)
        self.canvas.freeze()
            
    """Adjust the cell size of the specified grid in both directions equally."""
    def adjust_grid_spacing_2d(self, spacing_x: int, spacing_y: int, identifier = 0):
        self.grids[identifier].adjust_grid_spacing_2d(spacing_x, spacing_y)
        self.canvas.freeze()
            
    """Adjust the size of the specified grid by the provided amounts."""
    def adjust_grid_size(self, width_adjust: int, height_adjust: int, identifier = 0):
        #print(f"X: {width_adjust}, Y: {height_adjust}")
        self.grids[identifier].adjust_grid_size(width_adjust, height_adjust)
        self.canvas.freeze()

    """Resize the specified grid to the mouse cursor."""
    def adjust_grid_size_to_cursor(self, identifier = 0):
        self.grids[identifier].adjust_grid_size_to_mouse()
        self.canvas.freeze()
        
    """Adjust the specified grid by the specified amounts.""" 
    def adjust_grid_position(self, x_adjust: int, y_adjust: int, identifier = 0):
        self.grids[identifier].adjust_grid_position(x_adjust, y_adjust)
        self.canvas.freeze()

    """Move the specified grid to the mouse cursor."""
    def adjust_grid_position_to_mouse(self, identifier = 0):
        self.grids[identifier].adjust_grid_position_to_mouse()
        self.canvas.freeze()
        
    """Add a new grid with the specified attributes."""
    def add_grid(self, x: int, y: int, width: float, height: float, /, cell_width = 10, cell_height = 10):
        self.grids.append(self.FlexibleGrid(x, y, width, height, self.max_rect, cell_width, cell_height))

    """Delete every loaded grid."""
    def clear_grids(self):
        self.grids = []
        self.canvas.freeze()
        
    """Switch to the specified number grid."""
    def set_active_grid(self, grid = 0):
        self.active_grid = grid if (grid > 0 and grid < len(self.grids)) else 0
        self.canvas.freeze()

    """Print out the values of contained grids."""
    def dump_data(self):
        number = 0
        for grid in self.grids:
            print(f"Grid {number}: ({grid.get_info()})")
            number += 1
    
    """Copy commands to clipboard to generate the current grid layout."""
    def copy_preset(self):
        command = ""
        for grid in self.grids:
            command = command + grid.get_preset() + "\n"
        clip.set_text(command)
        
            
pixel_editor = PixelEditor(500, 500)
pixel_editor.enable()
pixel_editor.add_grid(300, 300, 500, 400, 30, 20) 
pixel_editor.add_grid(600, 300, 500, 400, 50, 50)
pixel_editor.add_grid(300, 200, 300, 400, 30, 30)

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
        """Turn on the pixel editor."""
        pixel_editor.enable()

    def pixel_editor_off():
        """Turn off the pixel editor."""
        pixel_editor.disable()

    def pixel_editor_toggle():
        """Turn on the pixel editor, or off if it is already on."""
        pixel_editor.toggle()

    def jump_to_grid(character: str, number: int):
        """Move the cursor to the indicated position."""
        x, y = pixel_editor.cell_coordinate(character, number)
        ctrl.mouse_move(x, y)
    
    def editor_adjust_position(number: int, direction: str):
        """Move the grid overlay by the specified amount."""
        x, y = interpret_direction(number, direction)
        pixel_editor.adjust_grid_position(x, y)
        
    def editor_adjust_position_2d(number: int, direction: str, number2: int, direction2: str):
        """Move the grid overlay by the specified amounts."""
        x, y = interpret_direction(number, direction)
        x2, y2 = interpret_direction(number2, direction2)  
        pixel_editor.adjust_grid_position(x + x2, y + y2)
        
    def editor_adjust_position_cursor():
        """Move the grid overly to cursor."""
        pixel_editor.adjust_grid_position_to_mouse()
        
    def editor_adjust_size(number: int, direction: str):
        """Resize the grid overlay by the specified amount."""
        x, y = interpret_direction(number, direction)
        pixel_editor.adjust_grid_size(x, y)
        
    def editor_adjust_size_2d(number: int, direction: str, number2: int, direction2: str):
        """Resize the grid overlay by the specified amounts."""
        x, y = interpret_direction(number, direction)
        x2, y2 = interpret_direction(number2, direction2)
        pixel_editor.adjust_grid_size(x + x2, y + y2)
        
    def editor_adjust_size_cursor():
        """Resize the grid overlay to the mouse cursor."""
        pixel_editor.adjust_grid_size_to_cursor()
                
    def editor_set_spacing(number: int):
        """Set the cell width and height, as a square grid."""
        pixel_editor.set_grid_spacing(number)
                
    def editor_set_spacing_2d(number: int, number2: int):
        """Set the cell width and height, as independent values."""
        pixel_editor.set_grid_spacing_2d(number, number2)
                
    def editor_adjust_spacing(number: int, direction: str):
        """Adjust the cell width and height, as a square grid."""
        x, y = interpret_direction(number, direction)
        pixel_editor.adjust_grid_spacing(x + y)
                
    def editor_adjust_spacing_2d(number: int, direction: str, number2: int, direction2: str):
        """Adjust the cell width and height, as independent values."""
        x, y = interpret_direction(number, direction)
        x2, y2 = interpret_direction(number2, direction2)
        pixel_editor.adjust_grid_spacing_2d(x + x2, y + y2)

    def add_grid(x: int, y: int, width: float, height: float, cell_width: int, cell_height: int):
        """Add a new grid with the specified values."""
        pixel_editor.add_grid(x, y, width, height, cell_width, cell_height)

    def clear_grids():
        """Delete every loaded grid."""
        pixel_editor.clear_grids()

    def change_grid(number: int):
        """Change to the specified grid number."""
        pixel_editor.set_active_grid(number)
        
    def dump_grid_data():
        """Print out the values of contained grids."""
        pixel_editor.dump_data()
        
    def copy_grid_data():
        """Copy the settings of the loaded grids."""
        pixel_editor.copy_preset()

ctx = Context()
ctx.lists['user.directional'] = [
    'up', 'down', 'right', 'left', 
]