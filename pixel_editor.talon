mode: user.pixel
-
#pixel editor:
#    user.pixel_editor_toggle()
    
# SET UP FUNCTIONS #
pixel (sell|cell|so) <number> square:
    user.editor_set_spacing(number)
pixel (sell|cell|so) <number> (by|buy) <number>:
    user.editor_set_spacing_2d(number_1, number_2)
pixel (sell|cell|so) <number> {user.directional} square:
    user.editor_adjust_spacing(number, directional)
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
    
pixel (off|offset) (russet|reset):
    user.editor_set_grid_offset(0, 0)
pixel (off|offset) <number> {user.directional}:
    user.editor_adjust_grid_offset(number_1, directional_1, 0, "up")
pixel (off|offset) <number> {user.directional} <number> {user.directional}:
    user.editor_adjust_grid_offset(number_1, directional_1, number_2, directional_2)
    
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
slide {user.directional}:
    user.move_on_grid(1, directional_1)
slide <number> {user.directional}:
    user.move_on_grid(number_1, directional_1)
slide {user.directional} {user.directional}:
    user.move_on_grid_2d(1, directional_1, 1, directional_2)
slide <number> {user.directional} {user.directional}:
    user.move_on_grid_2d(number, directional_1, number, directional_2)
slide <number> {user.directional} <number> {user.directional}:
    user.move_on_grid_2d(number_1, directional_1, number_2, directional_2)
pixel grid switch <number>:
    user.change_grid(number)
    # go to last stored position
    user.move_on_grid(0, "down")
pixel fast [on]:
    user.start_fast()
pixel fast (of|off):
    user.stop_fast()
    
# or  fix this - does not seem to update render even though value is changing
pixel grid opacity <number>:
    user.editor_set_opacity(number)
    
droll:
    user.cursor_drag()

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
# ability to offset the first row/column of a grid - COMPLETE

# jump to position on grid - COMPLETE
# move by grid cells - COMPLETE
# pixel mode - turns off extraneous commands - COMPLETE
# quick mode - say coordinates or directions without any prefix to move - command to turn on and off - COMPLETE
# HSV adjustment that can read in values - COMPLETE (room for improvement in precision)
# RGB adjustment that can read in values - CLOSED
# tool commands - COMPLETE
# dragging commands - COMPLETE
# stroke mode - whether to draw or just move

# translation modes - how the cursor moves from point a to point b (movement patterns via vector like data for custom rotations of shapes/brushes)
# anti-alliasing script / edge patterning 
# custom grid format for uneven grids
# automatic offset
# hexagonal grid
# isometric grid 