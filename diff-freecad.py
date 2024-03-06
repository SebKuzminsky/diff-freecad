#!/usr/bin/env freecadcmd

import argparse
import pathlib

import Mesh
import MeshPart
import Part


argparser = argparse.ArgumentParser(description=__doc__)
argparser.add_argument('FCSTD', help="FCStd file to meshify.")
args = argparser.parse_args()

fcstd = pathlib.Path(args.FCSTD)

doc = FreeCAD.openDocument(args.FCSTD)
mesh_obj = doc.addObject("Mesh::Feature", "Mesh")

for obj in doc.Objects:
    if obj.TypeId == 'PartDesign::Body':
        print(f"exporting {obj.Label}")
        mesh_obj.Mesh = MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=0.01)
        stl_filename = pathlib.Path(f"{fcstd.stem}-{obj.Label}.stl")
        Mesh.export([mesh_obj], str(stl_filename))
