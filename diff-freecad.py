#!/usr/bin/env freecadcmd

"Show a visual diff between two FCStd files."

import argparse
import pathlib
import sys

import Mesh
import MeshPart
import Part


def export_bodies(fcstd: pathlib.Path):
    doc = FreeCAD.openDocument(str(fcstd))
    mesh_obj = doc.addObject("Mesh::Feature", "Mesh")
    for obj in doc.Objects:
        if isinstance(obj, Part.BodyBase):
            mesh_obj.Mesh = MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=0.01)
            stl_filename = pathlib.Path(f"{fcstd.stem}-{obj.Label}.stl")
            Mesh.export([mesh_obj], str(stl_filename))


if len(sys.argv) == 2:
    # One argument, just export the Body objects to STL.
    fcstd = pathlib.Path(sys.argv[1])
    export_bodies(fcstd)

else:
    print("usage:")
    print("    diff-freecad FCSTD                  Export each Body to an STL file.")
    raise SystemExit("unknown command line arguments")
