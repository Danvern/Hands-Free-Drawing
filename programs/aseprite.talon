os: windows
and app.name: Aseprite - Animated sprites editor & pixel art tool
os: windows
and app.exe: Aseprite.EXE
os: windows
and app.name: Aseprite.exe
os: windows
and app.exe: Aseprite.exe
mode: user.pixel
-
settings():
    key_wait = 20.0
    key_hold = 20.0

# FILE #
file save : key(ctrl-s)
(enter|confirm) : key(enter)
(escape|cancel) : key(esc)

# DRAW #
brush (big|bigger|large|larger|grow) : key(=)
brush (small|smaller|shrink) : key(-)

# EDIT #
undo that : key(ctrl-z)  
redo that : key(ctrl-y)
cut that : key(ctrl-x)
copy that : key(ctrl-c)
paste that : key(ctrl-v)
select stroke : key(s)
select fill : key(f)
select all : key(ctrl-a)
select (cell|sell|so) : key(ctrl-t)
deselect : key(ctrl-d)
reselect : key(ctrl-shift-d)
select invert : key(ctrl-shift-i)
select (tile|till): 
    mouse_click(0)
    mouse_click(0)
# working with adding selections is going to require some more thought
delete: key(delete)
fill selection: key(f)

# TRANSFORMATION #
move up : key(up)
move <number> up: 
    user.repeat_key("up", number)
move down : key(down)
move <number> down:
    user.repeat_key("down", number)
move left : key(left)
move <number> left:
    user.repeat_key("left", number)
move right : key(right)
move <number> right:
    user.repeat_key("right", number)
flip horizontal : key(shift-h)
flip vertical : key(shift-v)
    
# TOOLS #
(tool|toll) options : user.jump_to_anchor(168, 82, 'top', 'left')
select square : key(m)
select circle : key(shift-m)
select lasso : key(q)
select lasso polly : key(shift-q)
select (wand|on|one) : key(w)
(pencil|brush) : key(b)
spray  : key(shift-b)
(erase|eraser) : key(e)
replace : key(shift-e)
(eyedrop|eyedropper) [left]:
    key(alt:down)
    mouse_click(0)
    key(alt:up)
(eyedrop|eyedropper) right:
    key(alt:down)
    mouse_click(1)
    key(alt:up)
move : key(v)
slice : key(shift-c)
(fill|pocket|bucket) : key(g)
gradient : key(shift-g)
line : key(l)
curve : key(shift-l)
rectangle : key(u)
(ellipse|circle) : key(shift-u)
contour : key(d)
polygon : key(shift-d)
(blur|jumble) : key(r)
text : key(t)
crop : key(c)

# NAVIGATION #
canvas grid : user.change_grid(0)
pan up : key(space:down up space:up)
pan <number> up:
    user.repeat_key("space-up", number)
pan down : key(space:down down space:up)
pan <number> down:
    user.repeat_key("space-down", number)
pan left : key(space:down left space:up)
pan <number> left:
    user.repeat_key("space-left", number)
pan right : key(space:down right space:up)
pan <number> right:
    user.repeat_key("space-right", number)
zoom one:
    user.buffer_keys()
    key(1)
    user.restore_keys()
    user.editor_set_spacing(1)
zoom two:
    user.buffer_keys()
    key(2)
    user.restore_keys()
    user.editor_set_spacing(2)
zoom three:
    user.buffer_keys()
    key(3)
    user.restore_keys()
    user.editor_set_spacing(4)
zoom four:
    user.buffer_keys()
    key(4)
    user.restore_keys()
    user.editor_set_spacing(8)
zoom five:
    user.buffer_keys()
    key(5)
    user.restore_keys()
    user.editor_set_spacing(16)
zoom six:
    user.buffer_keys()
    key(6)
    user.restore_keys()
    user.editor_set_spacing(32)

# COLOR #
color (swap|switch) : key(x)
color (next|right) : key(])
color (previous|left) : key([)
color grid : user.change_grid(1)
color wheel : user.jump_to_anchor(79, -189, 'bottom', 'left')
color (you|hue) <number> up:
    key(ctrl-alt-shift:down)
    #mouse_scroll(number, 0)
    user.scroll_amount(number)
    key(ctrl-alt-shift:up)
color (you|hue) <number> down:
    key(ctrl-alt-shift:down)
    user.scroll_amount(0 - number)
    key(ctrl-alt-shift:up)
color (saturation|that|sat) <number> up:
    key(ctrl-alt:down)
    user.scroll_amount(number)
    key(ctrl-alt:up)
color (saturation|that|sat) <number> down:
    key(ctrl-alt:down)
    user.scroll_amount(0 - number)
    key(ctrl-alt:up)
color (value|light|lightness) <number> up:
    key(ctrl-shift:down)
    user.scroll_amount(number)
    key(ctrl-shift:up)
color (value|light|lightness) <number> down:
    key(ctrl-shift:down)
    user.scroll_amount(0 - number)
    key(ctrl-shift:up)
color (opacity|fade) <number> up:
    key(ctrl-space:down)
    user.scroll_amount(number)
    key(ctrl-space:up)
color (opacity|fade) <number> down:
    key(ctrl-space:down)
    user.scroll_amount(0 - number)
    key(ctrl-space:up)
    
# TIMELINE #
(timeline|layer) grid : user.change_grid(2)
(lop|loop) section : key(f2)
onion [skin] : key(f3)

# ANIMATION #
animation play : key(enter)
frame (next|right) : key(right)
frame (previous|left) : key(left)
frame first : key(home)
frame last : key(and|end)
frame properties : key(p)
frame new : key(alt-n)
frame blank : key(alt-b)
frame duplicate : key(alt-d)
frame duplicate link : key(alt-m)
frame delete : key(alt-c)
frame reverse : key(alt-i)
frame go : key(alt-g)

# LAYERS #
layer (next|up) : key(up)
layer (previous|down) : key(down)
layer new : key(shift-n)
layer group : key(alt-shift-n)
layer copy : key(ctrl-j)
layer (hide|show) : key(shift-x)
layer (expand|contract) : key(shift-e)
layer full opacity : key(shift-4)
layer half opacity : key(shift-2)
layer quarter opacity : key(shift-1)

# VIEW #
timeline toggle : key(tag)
(palate|palette) editor : key(f4)
preview : key(f7)
preview full : key(f8)
toggle extra : key(ctrl-h)
toggle advanced : key(ctrl-f)
scroll to center : key(shift-z)

# GRID #
toggle (till|tile) grid : key(ctrl-')

# FX #
outline that : key(shift-o)
color replace : key(shift-r)
effect (you|hue|saturation) : key(ctrl-u)

# control space opacity
# control hue
# control alternate lightness
# control shift saturation