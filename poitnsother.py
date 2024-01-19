import adsk.core, adsk.fusion, traceback
import os
import ast

def run(context):
    radius_center_nautilus = 0.02
    
    ui = None
    try: 
        with os.open(str('C:\Users\\nicol\OneDrive\Documents\TU Eindhoven\Designing a lanching mechanism\CBL\gear_points.txt')) as pointsfile:
            points_nautilus = ast.literal_eval(str(pointsfile.read()))
        app = adsk.core.Application.get()
        ui = app.userInterface

        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = app.activeProduct

        rootComp = design.rootComponent

        sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)
        circles = sketch.sketchCurves.sketchCircles
        points = adsk.core.ObjectCollection.create()

        for p in range(len(points_nautilus)):
            points.add(adsk.core.Point3D.create(points_nautilus[p][0], points_nautilus[p][1], 0))
        for i in range(points.count-1):
            pt1 = points.item(i)
            pt2 = points.item(i+1)
            sketch.sketchCurves.sketchLines.addByTwoPoints(pt1, pt2)

        sketch.sketchCurves.sketchLines.addByTwoPoints(points.item(1), points.item(points.count-1))
        circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), radius_center_nautilus)
        


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))