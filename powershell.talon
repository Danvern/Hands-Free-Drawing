os: windows
and app.name: powershell.exe
os: windows
and app.exe: powershell.exe
-
get:'git '
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