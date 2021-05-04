pixel editor:
    user.pixel_editor_toggle()
    
# SET UP FUNCTIONS #
pixel (sell|cell|so) <number> square:
    user.editor_set_spacing(number)
pixel (sell|cell|so) <number> (by|buy) <number>:
    user.editor_set_spacing_2d(number_1, number_2)
pixel (sell|cell|so) <number> {user.directional} square:
    user.editor_adjust_spacing(number, directional)
# TODO - make an actual method for this
pixel (sell|cell|so) <number> {user.directional}:
    user.editor_adjust_spacing_2d(number, directional, 0, "up")
pixel (sell|cell|so) <number> {user.directional} (by|buy) <number> {user.directional}:
    user.editor_adjust_spacing_2d(number_1, directional_1, number_2, directional_2)
    
pixel size <number> {user.directional}:
    user.editor_adjust_size(number_1, directional_1)
pixel size <number> {user.directional} <number> {user.directional}:
    user.editor_adjust_size_2d(number_1, directional_1, number_2, directional_2)
pixel size (mouth|mouse|cursor):
    user.editor_adjust_size_cursor()    

pixel pose <number> {user.directional}:
    user.editor_adjust_position(number_1, directional_1)
pixel pose <number> {user.directional} <number> {user.directional}:
    user.editor_adjust_position_2d(number_1, directional_1, number_2, directional_2)
pixel pose (mouth|mouse|cursor):
    user.editor_adjust_position_cursor()
    
pixel dump grid data:
    user.dump_grid_data()
pixel copy grid data:
    user.copy_grid_data()

pixel load default:
    user.clear_grids()
    user.add_grid(166, 98, 1706, 632, 8, 8)
    user.add_grid(8, 99, 132, 635, 12, 12)
    user.add_grid(161, 768, 1725, 230, 23, 23)


# NAVIGATION #
cart <user.letter> <number>:
    user.jump_to_grid(letter, number)
pixel grid switch <number>:
    user.change_grid(number)
    
    
# TODO

# set up git - COMPLETE
    
# implement smooth grid positioning/resizing - COMPLETE
# implement independent width and height - COMPLETE
# implement preset grids for time line and palette - COMPLETE
# separate grid class - COMPLETE
# labels for positions on a grid - CLOSED
# ability to save per program presets for grid locations by exporting a command to clip board - COMPLETE
# multiple grids that can be switch between - COMPLETE
# preset cell sizes for zoom levels
# ability to offset the first row/column of a grid

# quick mode - say coordinates or directions without any prefix to move - command to turn on and off
# HSV adjustment that can read in values
# RGB adjustment that can read in valuesp
# translation modes - how the cursor moves from point a to point b (movement patterns)
# stroke mode - whether to draw or just move

# custom grid format for uneven grids
# automatic offset
# hexagonal grid
# isometric grid 