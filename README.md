This is a tool to visually diff FreeCAD FCStd files.  It integrates with
git, and is easy to run on the command line.

It uses FreeCAD's internal Python APIs to export each Body object to an
STL file, then uses stl_cmd to compute the diffs, and fstl to view them.

stl_cmd is available in Debian, and here: <https://github.com/AllwineDesigns/stl_cmd.git>

fstl is available in Debian, and here: <https://www.mattkeeter.com/projects/fstl/>, <https://github.com/fstl-app/fstl>


# Running by hand

`diff-freecad.py a.FCStd b.FCStd`


# Integrating with git

1.  In `~/.gitconfig` (global) or `.git/config` (per repo), add these lines:
```
    [diff "diff-freecad"]
        command=diff-freecad.py
```

2.  In `.gitattributes` in your repo, add this line:
```
    *.FCStd diff=diff-freecad
```

3. Run `git diff` like normal, e.g. `git diff a.FCStd` or `git diff v1.0..v1.1 -- a.FCStd`.
