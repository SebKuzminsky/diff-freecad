#!/usr/bin/env freecadcmd

"Show a visual diff between two FCStd files."

import pathlib
import subprocess
import sys
import tempfile

import FreeCAD
import Mesh
import MeshPart
import Part


def export_bodies(fcstd: pathlib.Path, dest_dir: pathlib.Path = None):
    doc = FreeCAD.openDocument(str(fcstd))
    mesh_obj = doc.addObject("Mesh::Feature", "Mesh")
    for obj in doc.Objects:
        if isinstance(obj, Part.BodyBase):
            mesh_obj.Mesh = MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=0.01)
            if dest_dir is None:
                stl_filename = pathlib.Path(f"{fcstd.stem}-{obj.Label}.stl")
            else:
                stl_filename = dest_dir / pathlib.Path(f"{fcstd.stem}-{obj.Label}.stl")
            Mesh.export([mesh_obj], str(stl_filename))


def diff_stl(old_stl: pathlib.Path, new_stl: pathlib.Path, temp_dir: pathlib.Path):
    print(f"diff stl {old_stl=} {new_stl=}")

    intersection_file = temp_dir / "intersection.stl"
    deleted_file = temp_dir / "deleted.stl"
    added_file = temp_dir / "added.stl"

    r = subprocess.run(
        ['stl_boolean', '-a', old_stl, '-b', new_stl, '-i', str(intersection_file)],
        check=True,
        capture_output=True
    )

    r = subprocess.run(
        ['stl_boolean', '-a', old_stl, '-b', new_stl, '-d', str(deleted_file)],
        check=True,
        capture_output=True
    )

    r = subprocess.run(
        ['stl_boolean', '-a', new_stl, '-b', old_stl, '-d', str(added_file)],
        check=True,
        capture_output=True
    )

    old_viewer = subprocess.Popen(
        ['fstl', str(old_stl)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    new_viewer = subprocess.Popen(
        ['fstl', str(new_stl)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    intersection_viewer = subprocess.Popen(
        ['fstl', str(intersection_file)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    deleted_viewer = subprocess.Popen(
        ['fstl', deleted_file],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    added_viewer = subprocess.Popen(
        ['fstl', added_file],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    old_viewer.wait()
    new_viewer.wait()

    intersection_viewer.wait()
    deleted_viewer.wait()
    added_viewer.wait()


def diff_fcstd(old_fcstd: pathlib.Path, new_fcstd: pathlib.Path):
    # Export all the new and old Bodies into a couple of temp directories.
    try:
        temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="diff-freecad."))

        old_path = pathlib.Path(temp_dir, "old")
        old_path.mkdir()
        export_bodies(old_fcstd, old_path)

        new_path = pathlib.Path(temp_dir, "new")
        new_path.mkdir()
        export_bodies(new_fcstd, new_path)

    except Exception as e:
        print(e)
        raise

    # Find old/new Bodies with matching names and diff their STLs.
    old_stls = list(old_path.glob('*.stl'))
    new_stls = list(new_path.glob('*.stl'))

    for old_stl in old_stls:
        new_stl = new_path / old_stl.name
        if new_stl in new_stls:
            print(f"{old_stl.name} is in both old and new")
            diff_stl(old_stl, new_stl, temp_dir)
        else:
            print(f"{old_stl.name} was removed in new")

    for new_stl in new_stls:
        old_stl = old_path / new_stl.name
        if old_stl in old_stls:
            # We handled this above already.
            pass
        else:
            print(f"{new_stl.name} was added in new")

#
# Debian Bookworm with Python 3.11:
#     sys.argv=['/home/seb/bin/diff-freecad.py', 'mount.FCStd', '/tmp/git-blob-j4PrAl/mount.FCStd', 'd41e8faebe37808cdfd5fb6a246fa55d7c041677', '100644', '/tmp/git-blob-oDo0Vs/mount.FCStd', 'a06df0ff0d6820643a7c76cfd4a878fddfb59f2b', '100644']
#     sys.orig_argv=['freecadcmd', '/home/seb/bin/diff-freecad.py', 'mount.FCStd', '/tmp/git-blob-j4PrAl/mount.FCStd', 'd41e8faebe37808cdfd5fb6a246fa55d7c041677', '100644', '/tmp/git-blob-oDo0Vs/mount.FCStd', 'a06df0ff0d6820643a7c76cfd4a878fddfb59f2b', '100644']
#
# Ubuntu 22.04 with Python 3.10:
#     sys.argv=['freecadcmd', '/home/seb/.local/bin/diff-freecad.py', 'mount.FCStd', '/tmp/vFqj42_mount.FCStd', 'a06df0ff0d6820643a7c76cfd4a878fddfb59f2b', '100644', 'mount.FCStd', '0000000000000000000000000000000000000000', '100644']
#     sys.orig_argv=[]
#
# Here we deal with all those options and make `args` into just the
# arguments *passed to* the script, not including the script name itself
# or its interpreter or anything like that.
#

if hasattr(sys, 'orig_argv') and len(sys.orig_argv) == 0:
    args = sys.argv[2:]
else:
    args = sys.argv[1:]

if len(args) == 1:
    # One argument, just export the Body objects to STL.
    fcstd = pathlib.Path(args[0])
    export_bodies(fcstd)

elif len(args) == 2:
    # Two arguments, the user is diffing by hand.
    old_fcstd = pathlib.Path(args[0])
    new_fcstd = pathlib.Path(args[1])
    diff_fcstd(old_fcstd, new_fcstd)

elif len(args) == 7:
    # Seven arguments, the user is diffing using git.  When run from
    # git you get these arguments:
    #     program_name path old-file old-hex old-mode new-file new-hex new-mode
    #
    # [
    #     'projects/programmable-power-supply/husb238/enclosure/enclosure-lid.stl',
    #     '/tmp/git-blob-Tfsy6e/enclosure-lid.stl',
    #     '85227db0e3a6d77cad95bb2aec1166afdb5af16b',
    #     '100644',
    #     'projects/programmable-power-supply/husb238/enclosure/enclosure-lid.stl',
    #     '0000000000000000000000000000000000000000',
    #     '100644'
    # ]
    old_fcstd = pathlib.Path(args[1])
    new_fcstd = pathlib.Path(args[4])
    diff_fcstd(old_fcstd, new_fcstd)

else:
    print("usage:")
    print("    diff-freecad FCSTD                  Export each Body to an STL file.")
    print()
    print("    diff-freecad OLD_FCSTD NEW_FCSTD    Export each Body of OLD and NEW to")
    print("                                        an STL, diff STLs visually.")
    raise SystemExit("unknown command line arguments")
