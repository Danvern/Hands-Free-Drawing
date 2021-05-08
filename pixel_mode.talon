not mode: sleep
-
mode pixel [on]:
    mode.disable("sleep")
    mode.disable("command")
    mode.disable("dictation")
    mode.enable("user.pixel")
    user.pixel_editor_on()
mode pixel (of|off):
    mode.disable("user.pixel")
    user.pixel_editor_off()
    mode.enable("command")