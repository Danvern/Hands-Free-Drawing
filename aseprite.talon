os: windows
and app.name: Aseprite.exe
os: windows
and app.exe: Aseprite.exe
-
settings():
    key_wait = 20.0
    key_hold = 20.0

# DRAW #
draw [left] : mouse_click(0)
draw right : mouse_click(1)
brush (big|bigger|large|larger|grow) : key(=)
brush (small|smaller|shrink) : key(-)

# EDIT #
#undo that : key(ctrl-z)  
#redo that : key(ctrl-y)
#cut that : key(ctrl-x)
#copy that : key(ctrl-c)
#paste that : key(ctrl-v)
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

# TRANSFORMATION #
move up : key(up)
move down : key(down)
move left : key(left)
move right : key(right)
flip horizontal : key(shift-h)
flip vertical : key(shift-v)
    
# TOOLS #
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
pan up : key(space:down up space:up)

# COLOR #
color (swap|switch) : key(x)
color grid : user.change_grid(1)
color (you|hue) <number> up:
    key(ctrl:down)
    #mouse_scroll(number, 0)
    user.scroll_amount(number)
    key(ctrl:up)
color (you|hue) <number> down:
    key(ctrl:down)
    user.scroll_amount(0 - number)
    key(ctrl:up)
color (saturation|that|sat) <number> up:
    key(ctrl-shift:down)
    user.scroll_amount(number)
    key(ctrl-shift:up)
color (saturation|that|sat) <number> down:
    key(ctrl-shift:down)
    user.scroll_amount(0 - number)
    key(ctrl-shift:up)
color (value|light|lightness) <number> up:
    key(ctrl-alt:down)
    user.scroll_amount(number)
    key(ctrl-alt:up)
color (value|light|lightness) <number> down:
    key(ctrl-alt:down)
    user.scroll_amount(0 - number)
    key(ctrl-alt:up)
color (opacity|fade) <number> up:
    key(ctrl-space:down)
    user.scroll_amount(number)
    key(ctrl-space:up)
color (opacity|fade) <number> down:
    key(ctrl-space:down)
    user.scroll_amount(0 - number)
    key(ctrl-space:up)
    
# TIMELINE #
timeline grid : user.change_grid(2)
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