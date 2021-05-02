pixel editor:
    user.pixel_editor_toggle()
pixel (sell|cell|so) <number>:
    user.editor_adjust_spacing(number)
pixel size <number> {user.directional}:
    user.editor_adjust_size(number_1, directional_1)
pixel size <number> {user.directional} <number> {user.directional}:
    user.editor_adjust_size_2d(number_1, directional_1, number_2, directional_2)
pixel pose <number> {user.directional}:
    user.editor_adjust_position(number_1, directional_1)
pixel pose <number> {user.directional} <number> {user.directional}:
    user.editor_adjust_position_2d(number_1, directional_1, number_2, directional_2)
pixel pose (mouth|mouse|cursor):
    user.editor_adjust_position_cursor()
cart <user.letter> <number>:
    user.jump_to_grid(letter, number)

# TODO

# set up git
    
# implement smooth grid positioning/resizing
# implement independent width and height
# implement preset grids for time line and palette
# separate grid class
# labels for positions on a grid
# ability to save per program presets for grid locations
# multiple grids that can be switch between
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