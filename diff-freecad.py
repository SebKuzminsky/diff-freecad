#!/usr/bin/env freecadcmd

"Show a visual diff between two FCStd files."

import argparse
import pathlib
import sys

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


if len(sys.argv) == 2:
    # One argument, just export the Body objects to STL.
    fcstd = pathlib.Path(sys.argv[1])
    export_bodies(fcstd)

else:
    print("usage:")
    print("    diff-freecad FCSTD                  Export each Body to an STL file.")
    raise SystemExit("unknown command line arguments")
