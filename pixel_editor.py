import math
from typing import Tuple
from talon import Context, Module, actions, canvas, cron, ctrl, screen, ui, clip
from talon.skia import Shader, Color, Paint, Rect                


modo = Module()
modo.list('directional', desc='Directions for expansion.')
modo.mode('pixel', desc='Enable editor commands.')
modo.tag('pixel_fast_mode', desc='Enable faster commands for drawing.')

ctx = Context()
ctx.lists['user.directional'] = [
    'up', 'down', 'right', 'left', 
]


class PixelEditor:
    def __init__(self, width: float, height: float):
        self.enabled = False
        self.canvas = None
        screen = ui.screens()[0]
        self.max_rect = screen.rect.copy()
        self.grids = []
        # self.grids = [self.FlexibleGrid(width, height, self.max_rect)]
        self.active_grid = 0
        self.grid_opacity = 0.05

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
            self.last_cell = (0, 0)
            self.offset_x = 0
            self.offset_y = 0
        
        """Return how many cells wide this grid is."""
        def get_cells_wide(self) -> int:
            return round(self.bounding_rect.width / self.cell_width)
        
        """Return how many cells tall this grid is."""
        def get_cells_tall(self) -> int:
            return round(self.bounding_rect.height / self.cell_height)
        
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

        """Set the offset of the grid to the specified amount."""
        def set_offset(self, x: int, y: int):
            self.offset_x = min(max(0, x), self.cell_width / 2)
            self.offset_y = min(max(0, y), self.cell_height / 2)
        
        """Adjust the offset of the grid by the specified amount."""
        def adjust_offset(self, x: int, y: int):
            remainder_x = (x + self.offset_x) % (self.cell_width / 2)
            remainder_y = (y + self.offset_y) % (self.cell_height / 2)
            self.set_offset(remainder_x, remainder_y)

        """Return whether the specified screen position is out of bounds of the grid."""
        def is_out_of_bounds(self, x: int, y: int) -> bool:
            x, y = self.screen_to_cell(x, y)
            if x < 0 or x >= self.get_cells_wide():
                return True
            if y < 0 or y >= self.get_cells_tall():
                return True
            return False
        
        """Return the cell coordinates of the specified screen position."""
        def screen_to_cell(self, x: int, y: int) -> Tuple[int, int]:
            # subtract grid position and divide by cell dimension ignoring remainder
            x = math.floor((x - self.bounding_rect.x - self.offset_x) / self.cell_width)
            y = math.floor((y - self.bounding_rect.y - self.offset_y) / self.cell_height)
            return x, y
        
        """Return the screen coordinates of the specified cell."""
        def cell_to_screen(self, x: int, y: int) -> Tuple[int, int]:
            # multiply by cell size and add half as an offset
            x = x * self.cell_width + self.cell_width * 0.5 + self.bounding_rect.x + self.offset_x
            y = y * self.cell_height + self.cell_height * 0.5 + self.bounding_rect.y + self.offset_y
            return x, y

        """Draw the graphical representation of the grid."""        
        def draw_canvas(self, canvas, opacity):
            paint = canvas.paint
            paint.color = Color(0 + 0 + (35 * 256) + 255 * opacity)
            # paint.color = '000055ff'
            rect = self.bounding_rect

            i_range = lambda start, stop, step: range(int(start), int(stop), int(step))
            paint.antialias = False
            # to make sure the left line renders (probably not necessary)
            base_offset = 1
            for x in i_range(rect.left + base_offset + self.offset_x, rect.right, self.cell_width):
                canvas.draw_line(x, rect.top, x, rect.bot)
            for y in i_range(rect.top + self.offset_y, rect.bot, self.cell_height):
                canvas.draw_line(rect.left, y, rect.right, y)        

        """Return a string of structural information."""        
        def get_info(self) -> str:
            r = self.bounding_rect
            return f"X: {r.x}, Y: {r.y}, Width: {r.width}, Height: {r.height}, Cell Width: {self.cell_width}, Cell Height: {self.cell_height}"
            
        """Return a command formatted as a string to generate this grid."""
        def get_preset(self) -> str:
            r = self.bounding_rect
            return f"user.add_grid({r.x}, {r.y}, {r.width}, {r.height}, {self.cell_width}, {self.cell_height})"

    """Draw the currently active grid."""
    def draw_canvas(self, canvas):
        if len(self.grids) > 0:
            self.grids[self.active_grid].draw_canvas(canvas, self.grid_opacity)

    """Return clamped grid cell coordinate from potentially out of bounds one."""
    def clamp_cell_coordinate(self, x: int, y: int, identifier = None) -> Tuple[int, int]:
        if identifier is None:
            identifier = self.active_grid
        x = min(max(0, x), self.grids[identifier].get_cells_wide())
        y = min(max(0, y), self.grids[identifier].get_cells_tall())
        return x, y

    """Return clamped grid cell coordinates of the specified screen position."""
    def screen_to_cell(self, x: int, y: int, identifier = None) -> Tuple[int, int]:
        if identifier is None:
            identifier = self.active_grid
        if self.grids[identifier].is_out_of_bounds(x, y):
            # print(f"{x}, {y} is out of bounds")
            return self.grids[identifier].last_cell
        else:
            return self.grids[identifier].screen_to_cell(x, y)

    """Return screen coordinates of the specified grid cell."""
    def cell_to_screen(self, x: int, y: int, identifier = None) -> Tuple[int, int]:
        if identifier is None:
            identifier = self.active_grid
        x, y = self.clamp_cell_coordinate(x, y, identifier)
        return self.grids[identifier].cell_to_screen(x, y)
        
    """Return coordinates adjusted by the specified number of grid cells."""
    def get_cell_adjusted(self, x: int, y: int, identifier = None) -> Tuple[int, int]:
        if identifier is None:
            identifier = self.active_grid
        last_x, last_y = self.screen_to_cell(*ctrl.mouse_pos(), identifier)
        return self.clamp_cell_coordinate(last_x + x, last_y + y, identifier)

    """Move the mouse cursor to the specified grid cell."""
    def move_cursor_to_cell(self, x: int, y: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].last_cell = x, y
        ctrl.mouse_move(*self.cell_to_screen(x, y, identifier))
    
    """Set the cell size of the specified grid in both directions equally."""
    def set_grid_spacing(self, spacing: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].set_grid_spacing(spacing)
        self.canvas.freeze()
            
    """Set the cell size of the specified grid in both directions equally."""
    def set_grid_spacing_2d(self, spacing_x: int, spacing_y: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].set_grid_spacing_2d(spacing_x, spacing_y)
        self.canvas.freeze()
            
    """Adjust the cell size of the specified grid in both directions equally."""
    def adjust_grid_spacing(self, spacing: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].adjust_grid_spacing(spacing)
        self.canvas.freeze()
            
    """Adjust the cell size of the specified grid in both directions equally."""
    def adjust_grid_spacing_2d(self, spacing_x: int, spacing_y: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].adjust_grid_spacing_2d(spacing_x, spacing_y)
        self.canvas.freeze()
            
    """Adjust the size of the specified grid by the provided amounts."""
    def adjust_grid_size(self, width_adjust: int, height_adjust: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        #print(f"X: {width_adjust}, Y: {height_adjust}")
        self.grids[identifier].adjust_grid_size(width_adjust, height_adjust)
        self.canvas.freeze()

    """Resize the specified grid to the mouse cursor."""
    def adjust_grid_size_to_cursor(self, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].adjust_grid_size_to_mouse()
        self.canvas.freeze()
        
    """Adjust the specified grid by the specified amounts.""" 
    def adjust_grid_position(self, x_adjust: int, y_adjust: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].adjust_grid_position(x_adjust, y_adjust)
        self.canvas.freeze()

    """Move the specified grid to the mouse cursor."""
    def adjust_grid_position_to_mouse(self, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].adjust_grid_position_to_mouse()
        self.canvas.freeze()
        
    """Set the offset of the specified grid."""
    def set_grid_offset(self, offset_x: int, offset_y: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].set_offset(offset_x, offset_y)
        self.canvas.freeze()
        
    """Adjust the offset of the specified grid."""
    def adjust_grid_offset(self, offset_x: int, offset_y: int, identifier = None):
        if identifier is None:
            identifier = self.active_grid
        self.grids[identifier].adjust_offset(offset_x, offset_y)
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
        
    """Set the opacity of the interface to the given value in percent form."""
    def set_opacity(self, opacity: int):
        self.opacity = max(min(opacity, 100), 0) / 100.0
            

        x = x * self.cell_size + self.cell_size * 0.5 + self.bounding_rect.x
        y = y * self.cell_size + self.cell_size * 0.5 + self.bounding_rect.y
        return x, y


"""Return integer coordinates from a character - integer combination."""
def interpret_coordinate(character: str, number: int) -> Tuple[int, int]:
    x = number
    # turn the character into a number, 97 is 'a'
    y = ord(character.lower()) - 97
    return x, y
    
"""Return integer vector from directional integer - string combination."""
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
        x, y = interpret_coordinate(character, number)
        x, y = pixel_editor.clamp_cell_coordinate(x, y)
        pixel_editor.move_cursor_to_cell(x, y)
        
    def move_on_grid(number: int, direction: str):
        """Move the cursor by the indicated amount of cells."""
        x, y = interpret_direction(number, direction)
        x, y = pixel_editor.get_cell_adjusted(x, y)
        pixel_editor.move_cursor_to_cell(x, y)
    
    def move_on_grid_2d(number: int, direction: str, number2: int, direction2: str):
        """Move the cursor by the indicated amount of cells."""
        x, y = interpret_direction(number, direction)
        x2, y2 = interpret_direction(number2, direction2)
        x, y = pixel_editor.get_cell_adjusted(x + x2, y + y2)
        pixel_editor.move_cursor_to_cell(x, y)
    
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

    def editor_set_grid_offset(offset_x: int, offset_y: int):
        """Set the offset of the specified grid."""
        pixel_editor.set_grid_offset(offset_x, offset_y)
        
    def editor_adjust_grid_offset(number: int, direction: str, number2: int, direction2: str):
        """Adjust the offset of the specified grid."""
        x, y = interpret_direction(number, direction)
        x2, y2 = interpret_direction(number2, direction2)
        pixel_editor.adjust_grid_offset(x + x2, y + y2)

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
        
    def editor_set_opacity(percent: int):
        """Set the opacity of the interface to the given value in percent form."""
        pixel_editor.set_opacity(percent)

    def cursor_drag():
        """Toggle dragging button."""
        button = 0
        pressed = button in ctrl.mouse_buttons_down()
        print(str(ctrl.mouse_buttons_down()))
        if not pressed:
            ctrl.mouse_click(button=button, down=True)
        else:
            ctrl.mouse_click(button=button, up=True)
        
    def scroll_amount(number: int):
        """Scroll the mouse wheel by the specified amount."""
        actions.mouse_scroll(number)
        
    def start_fast():
        """Initialize fast drawing mode."""
        ctx.tags = ['user.pixel_fast_mode']
        
    def stop_fast():
        """Stop fast drawing mode."""
        ctx.tags = []
        
            
pixel_editor = PixelEditor(500, 500)
pixel_editor.enable()
pixel_editor.add_grid(166, 98, 1706, 632, 8, 8)
pixel_editor.add_grid(8, 99, 132, 635, 12, 12)
pixel_editor.add_grid(161, 768, 1725, 230, 23, 23)