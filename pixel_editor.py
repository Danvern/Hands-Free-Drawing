import math, csv, os
from typing import Tuple
from talon import Context, Module, actions, canvas, cron, ctrl, screen, ui, clip, imgui, speech_system
from talon.skia import Shader, Color, Paint, Rect                


modo = Module()
modo.list('directional', desc='Directions for expansion.')
modo.list('anchor', desc='Directions for window anchors.')
modo.list('modifier_key', desc='Key modifiers.')
modo.mode('pixel', desc='Enable editor commands.')
modo.tag('pixel_fast_mode', desc='En0able faster commands for drawing.')
modo.tag('pixel_help_mode', desc='Enable commands for navigating the help panel.')

@modo.capture(rule="{user.modifier_key}+")
def modifiers(m) -> str:
    return "-".join(m.modifier_key_list)

ctx = Context()
ctx.lists['user.directional'] = [
    'up', 'down', 'right', 'left', 
]
ctx.lists['user.anchor'] = [
    'top', 'bottom', 'right', 'left', 'centre', 
]
ctx.lists['user.modifier_key'] = {
    'shift' : 'shift', 'control' : 'ctrl', 'alt' : 'alt', 'space' : 'space', 
}

keys_held = []
keys_held_buffer = []
keys_held_drag = []
verbose = True

# over engineered drawing code @Artificer111 - resident art cyborg
class PixelEditor:
    def __init__(self):
        self.enabled = False
        self.canvas = None
        self.grids = []
        # self.grids = [self.FlexibleGrid(width, height, self.max_rect)]
        self.active_grid = 0
        self.active_screen = 0
        screen = ui.screens()[self.active_screen]
        self.screen_bounds = screen.rect.copy()
        self.grid_opacity = 0.05

    """Reset drawing canvas and movement grid boundaries to be accurate to current screen."""
    def reset_bounds(self):
        screen = ui.screens()[self.active_screen]
        self.screen_bounds = screen.rect.copy()
        print(f"Screen Boundaries: {self.screen_bounds}")
        if self.canvas is not None:
            self.canvas.close()
        screen = ui.screens()[self.active_screen]
        self.canvas = canvas.Canvas(screen.x, screen.y, screen.width, screen.height)
        print(f"Canvas Boundaries: {screen}")
        self.canvas.register('draw', self.draw_canvas)
        self.canvas.freeze()

    def enable(self):
        if self.enabled:
            return
        self.enabled = True
        self.reset_bounds()
        
    def disable(self):
        if not self.enabled:
            return
        self.enabled = False
        self.canvas.close()
        self.canvas = None
        release_all()

    def toggle(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()
            
    class FlexibleGrid:
        def __init__(self, x: int, y: int, width: float, height: float, parent_editor, /, cell_width = 10, cell_height = 10):
            self.bounding_rect =  Rect(x, y, width, height)
            self.cell_width = cell_width
            self.cell_height = cell_height
            #self.max_rect = maximum_bounds
            #screen = ui.screens()[0]
            self.max_rect = lambda: parent_editor.get_bounds_rect()
            #if self.max_rect is None:
                #self.max_rect = screen.rect.copy()
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
            # print(self.get_info())
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
            # print(self.get_info())

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
            x = math.floor((x - self.max_rect().x - self.bounding_rect.x - self.offset_x) / self.cell_width)
            y = math.floor((y - self.max_rect().y - self.bounding_rect.y - self.offset_y) / self.cell_height)
            return x, y
        
        """Return the screen coordinates of the specified cell."""
        def cell_to_screen(self, x: int, y: int) -> Tuple[int, int]:
            # multiply by cell size and add half as an offset
            x = x * self.cell_width + self.cell_width * 0.5 + self.bounding_rect.x + self.offset_x + self.max_rect().x
            y = y * self.cell_height + self.cell_height * 0.5 + self.bounding_rect.y + self.offset_y + self.max_rect().y
            return x, y

        """Draw the graphical representation of the grid."""        
        def draw_canvas(self, canvas, opacity):
            paint = canvas.paint
            paint.color = Color(0 + 0 + (35 * 256) + 255 * opacity)
            # paint.color = '000055ff'
            rect = self.bounding_rect.copy()
            container = self.max_rect
            rect.x = rect.x + container().x
            rect.y = rect.y + container().y

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
            
        """Return a list of structural information."""        
        def get_info_list(self) -> []:
            r = self.bounding_rect
            return[r.x, r.y, r.width, r.height, self.cell_width, self.cell_height]
            
        """Return a command formatted as a string to generate this grid."""
        def get_preset(self) -> str:
            r = self.bounding_rect
            return f"user.add_grid({r.x}, {r.y}, {r.width}, {r.height}, {self.cell_width}, {self.cell_height})"

    """Draw the currently active grid."""
    def draw_canvas(self, canvas):
        if len(self.grids) > 0:
            self.grids[self.active_grid].draw_canvas(canvas, self.grid_opacity)

    """Return the bounding rectangle of the currently active screen."""
    def get_bounds_rect(self) -> Rect:
        return self.screen_bounds
        
    """Change the screen to display interface elements on."""
    def set_active_screen(self, screen_index: int):
        if screen_index >= 0 and screen_index < len(ui.screens()):
            self.active_screen = screen_index
            # screen = ui.screens()[self.active_screen]
            # self.screen_bounds = screen.rect.copy()
            print(f"Changed to screen {self.active_screen}")
            self.reset_bounds()
        else:
            print(f"Screen {screen_index} invalid. Retaining screen {self.active_screen}")

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
        self.grids.append(self.FlexibleGrid(x, y, width, height, self, cell_width, cell_height))

    """Delete every loaded grid."""
    def clear_grids(self):
        self.grids = []
        if self.canvas is not None:
            self.canvas.freeze()
        
    """Switch to the specified number grid."""
    def set_active_grid(self, grid = 0):
        self.active_grid = grid if (grid > 0 and grid < len(self.grids)) else 0
        self.move_cursor_to_cell(*self.grids[self.active_grid].last_cell)
        self.canvas.freeze()
        
    """Return the currently active grid."""
    def get_active_grid(self):
        return self.active_grid

    """Print out the values of contained grids."""
    def dump_data(self):
        number = 0
        for grid in self.grids:
            # print(f"Grid {number}: ({grid.get_info()})")
            number += 1
    
    """Copy commands to clipboard to generate the current grid layout."""
    def copy_preset(self):
        command = ""
        for grid in self.grids:
            command = command + grid.get_preset() + "\n"
        clip.set_text(command)
        
    """Copy data to csv to generate the current grid layout."""
    def copy_preset_csv(self):
        dir = os.path.join(os.path.dirname(__file__), 'pixel_grids.csv')
        with open(dir, 'w', newline='') as csvfile:
            fieldnames = ['x', 'y', 'width', 'height', 'cell_width', 'cell_height']
            writer = csv.writer(csvfile)
            # writer.writerow(fieldnames)
            for grid in self.grids:
                writer.writerow(grid.get_info_list())
                
    """Load data from file to generate a new grid layout."""
    def load_preset_csv(self):
        dir = os.path.join(os.path.dirname(__file__), 'pixel_grids.csv')
        with open(dir, newline='') as csvfile:
            reader = csv.reader(csvfile)
            self.clear_grids()
            for row in reader:
                data = list(map(int, row))
                self.add_grid(*data)
                
    """Set the opacity of the interface to the given value in percent form."""
    def set_opacity(self, opacity: int):
        self.opacity = max(min(opacity, 100), 0) / 100.0
            

        x = x * self.cell_size + self.cell_size * 0.5 + self.bounding_rect.x
        y = y * self.cell_size + self.cell_size * 0.5 + self.bounding_rect.y
        return x, y
        
        
# Here be dragons, giant documentation section ahead.
program_category_map = {}
category_command_map = {}
current_category = None
current_command = -1
help_text = []

def ready_documentation():    
    program_context_map = {}
    command_context_map = {}
    # obtain context for editor commands (+aseprite)
    for context_name, context in registry.contexts.items():
        short_name = ""
        splits = context_name.split(".")
        index = -1
        if "talon" in splits[index]:
            index = -2
            short_name = splits[index].replace("_", " ")
        else:
            short_name = splits[index].replace("_", " ")
        if short_name == "pixel editor" or short_name == "aseprite":
            program_context_map[short_name] = context
            command_context_map[short_name] = []
    
    for name, context in program_context_map.items():
        for value in context.commands.values():
            command_context_map[name].append(str(value.rule.rule))
            
    
    # open csv file (if it does not exist - lazy override prevention)
    with open("documentation.csv", 'w', newline='') as f:
        fieldnames = ['program', 'command']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for program, commands in command_context_map.items():
            for format in commands:
                writer.writerow({'program': program, 'command': format})
            
        
    # loop through context to process commands
    
    # for each command add to csv file (program + format, leave name description and the category blank)
    # close csv file
    pass
    
def load_documentation():
    # prepared dictionary (ordered) of context containing categories
    # prepared dictionary of categories containing commands
    # open csv file for reading
    # load in the predefined list
    # clothes file
    global program_category_map
    global category_command_map
    # print(program_category_map.get('air'))
    dir = os.path.join(os.path.dirname(__file__), 'pixel_documentation.csv')
    with open(dir, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        n = 0
        for row in reader:
            # print(row)
            if n > 0:
                if program_category_map.get(row['program']) is None:
                    categories = {}
                    program_category_map[row['program']] = categories
                if program_category_map[row['program']].get(row['category']) is None:
                    program_category_map[row['program']][row['category']] = []
                    category_command_map[row['category']] = []
                program_category_map[row['program']][row['category']].append({'command': row['command'], 'name': row['name'], 'description': row['description']})
                category_command_map[row['category']].append({'command': row['command'], 'name': row['name'], 'description': row['description']})
            n += 1 
    
def display_documentation():
    # check category
    # chuck selected command
    # of options are not negative assume selected
    # display in basic window
    global current_category
    global current_command
    global program_category_map
    global help_text
    help_text = []
    n = 1
    if current_category is None:
        # print(program_category_map or )
        for categoryDict in program_category_map.values():
            # print('test')
            for category in categoryDict.keys():
                # print(category)
                help_text.append(f"{n}. {category}")
                n += 1
    elif current_command < 0:
        for command in category_command_map[current_category]:
            help_text.append(f"{n}. {command['command']}")
            n += 1
    else:
        for information in category_command_map[current_category][current_command].values():
            help_text.append(information)
    
def select_number_command(number: int):
    # check what is selected
    # go one level down
    global current_category
    global current_command
    if current_category is None:
        if number >= 0 or number < len(help_text):
            # print(category_command_map.keys())
            current_category = list(category_command_map.keys())[number - 1]
    else:
        if number >= 0 or number < len(help_text):
            current_command = number - 1
    display_documentation()
    
def reset_documentation():
    # reset all selective value
    global current_category
    global current_command
    current_category = None
    current_command = -1
    display_documentation()
    
def go_back():
    # go back one level documentation
    global current_category
    global current_command
    if current_command > -1:
        current_command = -1
    else:
        current_category = None
    display_documentation()
    
@imgui.open(y=0)
def help_bar(gui: imgui.GUI):
    gui.text("PE Help")
    gui.line()
    global help_text
    for text in help_text:
        gui.text(text)
        
load_documentation()
# display_documentation()
# help_bar.show()
# select_number_command(13)
# select_number_command(1)
# print(ctx.tags)
# ready_documentation()
    
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
        
"""Return relative position of the cursor to the currently active window."""
def get_window_cursor_position() -> Tuple[int, int]:
    window = ui.active_window().rect
    return ctrl.mouse_pos()[0] - window.x, ctrl.mouse_pos()[1] - window.y
        
"""Return cursor position relative to specified anchor point."""
def get_position_from_anchor(vertical: str, horizontal: str) -> Tuple[int, int]:
    x, y = get_window_cursor_position()
    window = ui.active_window().rect
    if vertical == 'top':
        #  Do nothing as coordinates are already relative to top left point.
        pass
    elif vertical == 'bottom':
        y -= window.height
    else:
        # Assume center / middle.
        y -= window.height / 2
    if horizontal == 'left':
        #  Do nothing as coordinates are already relative to top left point.
        pass
    elif horizontal == 'right':
        x -= window.width
    else:
        # Assume center / middle.
        x -= window.width / 2
    return x, y
    
"""Move the cursor to the specified point relative to the specified anchor."""
def set_position_from_anchor(x: int, y: int, vertical: str, horizontal: str):
    window = ui.active_window().rect
    x, y = x + window.x, y + window.y
    if vertical == 'top':
        pass
    elif vertical == 'bottom':
        y += window.height
    elif vertical == 'centre':
        y += window.height / 2
    if horizontal == 'left':
        pass
    elif horizontal == 'right':
        x += window.width
    elif horizontal == 'centre':
        x += window.width / 2
    ctrl.mouse_move(x, y)

"""Generate command to move purser relative to anchor and copy it to clipboard."""
def dump_anchor_command(vertical: str, horizontal: str):
    x, y = get_position_from_anchor(vertical, horizontal)
    command = f"user.jump_to_anchor({x}, {y}, '{vertical}', '{horizontal}')"
    clip.set_text(command)
        
last_command = None

def parse_phrase(phrase):
    return " ".join(word.split("\\")[0] for word in phrase)


def on_phrase(p):
    global last_command
    try:
        val = parse_phrase(getattr(p["parsed"], "_unmapped", p["phrase"]))
    except:
        val = parse_phrase(p["phrase"])
    if val != "":
        last_command = val
        
speech_system.register('phrase', on_phrase)
        
@imgui.open(y=0)
def status_bar(gui: imgui.GUI):
    global last_command
    global verbose
    
    gui.text(("Pixel Editor" if pixel_editor.enabled else "INACTIVE") + " " + f"(Grid: {pixel_editor.get_active_grid()})")
    gui.text(last_command)
    if verbose:
        gui.text(f"Screen: {pixel_editor.active_screen}, Grid: {pixel_editor.get_active_grid()}, Mouse: {ctrl.mouse_pos()}")
        gui.text(f"{pixel_editor.grids[pixel_editor.get_active_grid()].get_info()}")
    gui.line()
    if "user.pixel_fast_mode" in ctx.tags:
        gui.text("FAST")
    if len(ctrl.mouse_buttons_down()) > 0:
        mouse_dictionary = {
            0: "left",
            1: "right",
            2: "middle",
            3: "side up",
            4: "side down",
        }
        mouse_status = "M: "
        for button in ctrl.mouse_buttons_down():
            mouse_status = mouse_status + mouse_dictionary[button] + ", "
        gui.text(mouse_status)
    global keys_held
    if len(keys_held) > 0:
        key_status = "K: "
        for key in keys_held:
            key_status = key_status + key + ", "
        gui.text(key_status)
        
"""Release any keys currently held by the program."""
def release_all():
    global keys_held
    if len(keys_held) > 0:
        for key in keys_held:
            ctrl.key_press(key=key, down=False)
        keys_held.clear()
    mouse_held = ctrl.mouse_buttons_down()
    if len(mouse_held) > 0:
        for button in mouse_held:
            ctrl.mouse_click(button=button, up=True)
        
"""Release any keys currently held by the program and buffer them to be restored later."""
def buffer_keys():
    global keys_held
    global keys_held_buffer
    keys_held_buffer = keys_held
    if len(keys_held) > 0:
        for key in keys_held:
            ctrl.key_press(key=key, down=False)
        keys_held.clear()
        
"""Restore any keys currently held by the key buffer."""
def restore_keys():
    global keys_held
    global keys_held_buffer
    if len(keys_held_buffer) > 0:
        for key in keys_held_buffer:
            ctrl.key_press(key=key, down=True)
        keys_held = keys_held_buffer
    keys_held_buffer = []

"""Toggle the specified keys."""
def toggle_keys(keys: []):
    global keys_held
    for key in keys:
        if key in keys_held:
            ctrl.key_press(key=key, down=False)
            keys_held.remove(key)
        else:
            ctrl.key_press(key=key, down=True)
            keys_held.append(key)

"""Toggle the held modifier keys triggered by a drag cursor action."""
def toggle_drag_keys():
    global keys_held_drag
    if len(keys_held_drag) > 0:
        toggle_keys(keys_held_drag)
        keys_held_drag = []
    
"""Release any active mouse buttons."""
def release_mouse_buttons():
    for other in ctrl.mouse_buttons_down():
        ctrl.mouse_click(button=other, up=True)
    toggle_drag_keys()
        
@modo.action_class
class Actions:
    def pixel_editor_on():
        """Turn on the pixel editor."""
        pixel_editor.enable()

    def pixel_editor_off():
        """Turn off the pixel editor."""
        pixel_editor.disable()
        release_all()

    def pixel_editor_toggle():
        """Turn on the pixel editor, or off if it is already on."""
        pixel_editor.toggle()

    def jump_to_grid(character: str, number: int):
        """Move the cursor to the indicated position."""
        x, y = interpret_coordinate(character, number)
        x, y = pixel_editor.clamp_cell_coordinate(x, y)
        pixel_editor.move_cursor_to_cell(x, y)
        
    def jump_to_grid_n(x: int, y: int):
        """Move the cursor to the indicated position."""
        x, y = pixel_editor.clamp_cell_coordinate(x, y)
        pixel_editor.move_cursor_to_cell(x, y)
        
    def jump_to_anchor(x: int, y: int, vertical: str, horizontal: str):
        """Move the cursor to the anchored position."""
        set_position_from_anchor(x, y, vertical, horizontal)
        
    def dump_anchor(vertical: str, horizontal: str):
        """Generate command to move cursor relative to anchor and copy it to clipboard."""
        dump_anchor_command(vertical, horizontal)
        
    def move_free(number: int, direction: str):
        """Move the cursor independently from the grid."""
        x, y = interpret_direction(number, direction)
        x, y = x + ctrl.mouse_pos()[0], y + ctrl.mouse_pos()[1]
        ctrl.mouse_move(x, y)
                
    def move_free_2d(number: int, direction: str, number2: int, direction2: str):
        """Move the cursor independently from the grid."""
        x, y = interpret_direction(number, direction)
        x2, y2 = interpret_direction(number2, direction2)
        x, y = x + x2 + ctrl.mouse_pos()[0], y + y2 + ctrl.mouse_pos()[1]
        ctrl.mouse_move(x, y)
        
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

    def editor_active_screen(index: int):
        """Change the screen to display interface elements on."""
        pixel_editor.set_active_screen(index)

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
        
    def load_grid_preset():
        """Load the saved grid settings."""
        pixel_editor.load_preset_csv()
    
    def save_grid_preset():
        """Save the current grid settings."""
        pixel_editor.copy_preset_csv()
        
    def editor_set_opacity(percent: int):
        """Set the opacity of the interface to the given value in percent form."""
        pixel_editor.set_opacity(percent)

    def cursor_drag(modifiers: str, button: int):
        """Toggle dragging button."""
        global keys_held_drag
        
        pressed = button in ctrl.mouse_buttons_down()
        # print(str(ctrl.mouse_buttons_down()))
        if not pressed:
            for other in ctrl.mouse_buttons_down():
                if other != button:
                    ctrl.mouse_click(button=other, up=True)
                    toggle_drag_keys()
                    return
            if modifiers != '':
                modifiers = modifiers.split("-")
                toggle_keys(modifiers)
                keys_held_drag = modifiers
            ctrl.mouse_click(button=button, down=True)
        else:
            ctrl.mouse_click(button=button, up=True)
            toggle_drag_keys()
            
    def toggle_drag_keys():
        """Toggle the held modifier keys triggered by a drag cursor action."""
        toggle_drag_keys()
            
    def release_mouse_buttons():
        """Release any active mouse buttons."""
        release_mouse_buttons()
        
    def scroll_amount(number: int):
        """Scroll the mouse wheel by the specified amount."""
        actions.mouse_scroll(number)
        
    def repeat_key(key: str, number: int):
        """Press the specifi5ed key for the specified amount of times."""
        space = shift = ctrlk = alt = False
        for word in key.split('-'):
            if word == 'space': 
                space = True
            elif word == 'shift':
                shift = True
            elif word == 'ctrl':
                ctrlk = True
            elif word == 'alt':
                alt = True
            else:
                base_key = word
        if space:
            while number > 0:
                ctrl.key_press(key="space", down=True)
                ctrl.key_press(key=base_key, shift=shift, ctrl=ctrlk, alt=alt)
                ctrl.key_press(key="space", down=False)
                number -= 1
        while number > 0:
            ctrl.key_press(key=base_key, shift=shift, ctrl=ctrlk, alt=alt)
            number -= 1
        
    def toggle_key(key_string: str):
        """Toggle holding down the specified key."""
        keys = key_string.split("-")
        toggle_keys(keys)

    def release_all_keys():
        """Release any keys currently held by the program."""
        release_all()
        
    def buffer_keys():
        """Release any keys currently held by the program and buffer them to be restored later."""
        buffer_keys()
    
    def restore_keys():
        """Restore any keys currently held by the key buffer."""
        restore_keys()
        
    def start_fast():
        """Initialize fast drawing mode."""
        ctx.tags.add('user.pixel_fast_mode')
        # This is necessary to make the system recognize that the list has been modified.
        ctx.tags = ctx.tags
        
    def stop_fast():
        """Stop fast drawing mode."""
        ctx.tags.discard('user.pixel_fast_mode')
        # This is necessary to make the system recognize that the list has been modified.
        ctx.tags = ctx.tags
        
    def status_toggle():
        """Toggle viewing the status panel."""
        if status_bar.showing:
            status_bar.hide()
        else:
            status_bar.show()

    def status_enable():
        """Enable the status panel."""
        status_bar.show()

    def status_disable():
        """Disable the status panel."""
        status_bar.hide()
        
    def pixel_help_toggle():
        """Toggle viewing the help panel."""
        if help_bar.showing:
            reset_documentation()
            help_bar.hide()
            ctx.tags.discard('user.pixel_help_mode')
            # This is necessary to make the system recognize that the list has been modified.
            ctx.tags = ctx.tags
            # print(ctx.tags)
        else:
            help_bar.show()
            display_documentation()
            ctx.tags.add('user.pixel_help_mode')
            # This is necessary to make the system recognize that the list has been modified.
            ctx.tags = ctx.tags
            # ctx.tags = ["user.pixel_help_mode"]
            # print(ctx.tags)
            
    def pixel_help_enable():
        """Enable the help panel."""
        help_bar.show()
        ctx.tags = ['user.pixel_help_mode']
        # ctx.tags.add('user.pixel_help_mode')
    
    def pixel_help_disable():
        """Disable the help panel."""
        reset_documentation()
        help_bar.hide()
        ctx.tags = []
        # ctx.tags.discard('user.pixel_help_mode')
        
    def pixel_help_select(number: int):
        """Displayed number topic."""
        select_number_command(number)
        
    def pixel_help_back():
        """Go back to to the previous that of topics."""
        go_back()
        
    def toggle_verbose():
        """Toggle displaying extra diagnostic data."""
        global verbose
        if verbose:
            verbose = False
        else:
            verbose = True

            
pixel_editor = PixelEditor()
# pixel_editor.enable()
# pixel_editor.add_grid(166, 98, 1706, 632, 8, 8)
# pixel_editor.add_grid(8, 99, 132, 635, 12, 12)
# pixel_editor.add_grid(161, 768, 1725, 230, 23, 23)
# pixel_editor.copy_preset_csv()
pixel_editor.load_preset_csv()
status_bar.show()