os: windows
and app.name: powershell.exe
os: windows
and app.exe: powershell.exe
os: windows
and app.name: Windows PowerShell
os: windows
and app.exe: PowerShell.exe
-
get:'git '
get commit all:
    'git commit -a'
    key(enter)
get (status|state):
    'git status'
    key(enter)
get short (status|state):
    "git status -s"
    key(enter)
get (add|plus):'git add '
get (change|changes):
    "git diff"
    key(enter)
get staged (change|changes):
    "git diff --staged"
    key(enter)
get log:
    "git log"
    key(enter)
get patch log:
    "git log -p"
    key(enter)