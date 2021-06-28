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
    
#undocumented
pixel screen <number>:
    user.editor_active_screen(number)
    
pixel dump grid data:
    user.dump_grid_data()
pixel copy grid data:
    user.copy_grid_data()

pixel load default:
    user.load_grid_preset()
pixel save default:
    user.save_grid_preset()

# NAVIGATION #
cart <user.letter> <number>:
    user.jump_to_grid(letter, number)
cart <number> (by|and) <number>:
    user.jump_to_grid_n(number, number)
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
anchor dump {user.anchor} {user.anchor}:
    user.dump_anchor(anchor_1, anchor_2)
#anchor test:
#    user.jump_to_anchor(-321, -620, 'bottom', 'right')

# MOUSE #
track : user.cursor_drag("", 0)
track side : user.cursor_drag("", 1)
draw:
    user.release_mouse_buttons()
    mouse_click(0)
draw side:
    user.release_mouse_buttons()
    mouse_click(1)
<user.modifiers> track : user.cursor_drag("{modifiers}", 0)
<user.modifiers> track side : user.cursor_drag("{modifiers}", 1)
<user.modifiers> draw:
    user.release_mouse_buttons()
    key("{modifiers}:down")
    mouse_click(0)
    key("{modifiers}:up")
<user.modifiers> draw side:
    user.release_mouse_buttons()
    key("{modifiers}:down")
    mouse_click(1)
    key("{modifiers}:up")
sneak <number> {user.directional}:
    user.move_free(number_1, directional_1)
sneak <number> {user.directional} <number> {user.directional}:
    user.move_free_2d(number_1, directional_1, number_2, directional_2)

# MODIFIER #
#hold shift: user.toggle_key("shift")
#hold control: user.toggle_key("ctrl")
#hold space: user.toggle_key("space")
#hold (all|alternate): user.toggle_key("alt")
hold <user.modifiers> : user.toggle_key("{modifiers}")

# REPEAT #
(repeat that|twice): core.repeat_command(1)
repeat that <number_small> [times]: core.repeat_command(number_small)

# INTERFACE #
pixel status: user.status_toggle()    
# or  fix this - does not seem to update render even though value is changing
pixel grid opacity <number>:
    user.editor_set_opacity(number)
help: user.pixel_help_toggle()

# I TRACKER # -undocumented
control mouse: user.mouse_toggle_control_mouse()
zoom mouse: user.mouse_toggle_zoom_mouse()

# TODO

# set up git - COMPLETE
    
# implement smooth grid positioning/resizing - COMPLETE
# implement independent width and height - COMPLETE
# implement preset grids for time line and palette - COMPLETE
# separate grid class - COMPLETE
# labels for positions on a grid - CLOSED
# ability to save per program presets for grid locations by exporting a command to clip board - COMPLETE
# multiple grids that can be switch between - COMPLETE
# preset cell sizes for zoom levels - COMPLETE
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
# fixed and dynamic way points for quick drawing of lines and curves
# holding modifier keys for increased tool functionality - COMPLETE
# make click and drag commands program non specific - COMPLETE
# make hold keys program non specific - COMPLETE
# relief all keys when pixel editor is turned off - COMPLETE
# relief all keys when pushed to talk is turned off - COMPLETE
# unbound mouse movement commands - COMPLETE
# toll options cursor jump point - COMPLETE
# color well cursor jump point - COMPLETE
# jump cursor when the current grid is changed - COMPLETE
# drag command stopped whatever drag is active instead of allowing too with once - COMPLETE

# hope file interactive version - COMPLETE
# integrated command history with status - COMPLETE
# states shows active grid, help, or if mode is inactive - COMPLETE
# clean start state - COMPLETE
# read me - quick start - COMPLETE
# licensing - COMPLETE
# github
# aseprite settings file (and instructions on how the color wheel needs to be set up+) - COMPLETE

# translation modes - how the cursor moves from point a to point b (movement patterns via vector like data for custom rotations of shapes/brushes)
# anti-alliasing script / edge patterning 
# custom grid format for uneven grids
# automatic offset
# hexagonal grid
# isometric grid 