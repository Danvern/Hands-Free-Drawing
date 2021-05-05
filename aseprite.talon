os: windows
and app.name: Aseprite.exe
os: windows
and app.exe: Aseprite.exe
-
settings():
    key_wait = 20.0
    key_hold = 20.0
    
# TOOLS #
select square : key(m)
select circle : key(shift-m)
line : key(l)

# NAVIGATION #
pan up : key(space:down up space:up)

# COLOR #
color (you|hue) <number> up:
    key(ctrl:down)
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
    

# control space opacity
# control hue
# control alternate lightness
# control shift saturation