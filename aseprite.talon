os: windows
and app.name: Aseprite.exe
os: windows
and app.exe: Aseprite.exe
-
settings():
    key_wait = 20.0
    key_hold = 20.0
select square : key(m)
select circle : key(shift-m)
line : key(l)
trip up : key(space:down up space:up)