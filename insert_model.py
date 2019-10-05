import bpy
import mathutils
import sys
import math
argv = []
try:
    argv = sys.argv[sys.argv.index("--") + 1:]
except:
    pass

MODEL_FILE = "C:\\path\\to\\models\\teeth.dae"
MODEL_ROTATE = 0
MODEL_FLIP = 0

script = bpy.data.texts["MODEL_SETUP_CONFIG"]
exec(script.as_string())

if len(argv):
    # handle filename input
    MODEL_FILE = argv[0]
if len(argv)>1:
    # handle flip=90
    MODEL_FLIP = 0 if argv[1][0:4] != 'flip' else int(argv[1][5:])
if len(argv)>2:
    # handle rotate=90
    MODEL_ROTATE = 0 if argv[2][0:6] != 'rotate' else int(argv[2][7:])

objs = bpy.data.objects
mats = bpy.data.materials
for objname in MODEL_SETUP_CONFIG["remove"]:
    bpy.data.objects.remove(bpy.data.objects[objname], do_unlink=True)
objectsBaseScene = bpy.data.objects.keys()
materialsBaseScene = bpy.data.materials.keys()

# Load the model, must only contain the mesh
model = None
bpy.ops.wm.collada_import(filepath=MODEL_FILE)

# keep only new meshes
additionalObjects = list(set(bpy.data.objects.keys()).difference(set(objectsBaseScene)))
additionalMaterials = list(set(bpy.data.materials.keys()).difference(set(materialsBaseScene)))
for objname in additionalObjects:
    if(bpy.data.objects[objname].type != 'MESH'):
        objs.remove(bpy.data.objects[objname], do_unlink=True)
    else:
        model = bpy.data.objects[objname]
for matname in additionalMaterials:
    mats.remove(bpy.data.materials[matname], do_unlink=True)

def applyNormalizedBoundingBox(boundingbox, model):
    # camera viewport height most important
    largest = max(model.dimensions.x, model.dimensions.y, model.dimensions.z)
    if(largest == model.dimensions.x):        
        aspectRatio = boundingbox.x / model.dimensions.x
    if(largest == model.dimensions.y):
        aspectRatio = boundingbox.y / model.dimensions.y
    if(largest == model.dimensions.z):        
        aspectRatio = boundingbox.z / model.dimensions.z
    model.scale = (aspectRatio, aspectRatio, aspectRatio)
    return model

def demoBoundingBox(model):
    # https://blenderartists.org/t/generate-bounding-boxes-for-selected-objects/559218
    minx = model.bound_box[0][0]
    maxx = model.bound_box[4][0]
    miny = model.bound_box[0][1]
    maxy = model.bound_box[2][1]
    minz = model.bound_box[0][2]
    maxz = model.bound_box[1][2]
    dx = maxx - minx
    dy = maxy - miny
    dz = maxz - minz
    new_name = 'BB{0}'.format(model.name)
    loc =  mathutils.Vector(((minx + 0.5* dx), (miny + 0.5* dy), (minz + 0.5* dz)))
    loc.rotate(model.rotation_euler)
    loc = loc + model.location
    # adding the bounding box cube
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=model.rotation_euler)
    new_obj = bpy.context.object
    new_obj.name = new_name
    new_obj.dimensions = mathutils.Vector((dx, dy, dz))
    # apply real scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    new_obj.scale = model.scale
    # both origins to same location
    model.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    new_obj.select_set(True)    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    # hide in viewpot and at rendering
    bpy.context.object.hide_render = True
    bpy.context.object.hide_viewport = True
    #new_obj.location = model.location
    return new_obj

if model:
    model.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    # rotate before applying cube dimensions
    if MODEL_ROTATE>0:
        model.rotation_euler = mathutils.Vector((0.0, 0.0, math.radians(MODEL_ROTATE)))
    if MODEL_FLIP>0:
        model.rotation_euler = mathutils.Vector((math.radians(MODEL_FLIP), 0.0, 0.0))
    if (MODEL_ROTATE>0 and MODEL_FLIP>0):
        model.rotation_euler = mathutils.Vector((math.radians(MODEL_FLIP), 0.0, math.radians(MODEL_ROTATE)))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
	# object_add() results in invalid context
    """
    if MODEL_SETUP_CONFIG["physics"]:
        bpy.ops.rigidbody.object_add()
        bpy.context.object.rigid_body.type = 'ACTIVE'
        bpy.context.object.rigid_body.collision_shape = 'MESH'
    """
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    targetLocation = MODEL_SETUP_CONFIG["position"]
    targetBoundingbox = MODEL_SETUP_CONFIG["boundariesBox"]
    simpleRef = demoBoundingBox(model)
    constraintCT = model.constraints.new('COPY_TRANSFORMS')
    constraintCT.target = simpleRef
    applyNormalizedBoundingBox(targetBoundingbox, simpleRef)
    simpleRef.location = mathutils.Vector((targetLocation.x, targetLocation.y, simpleRef.dimensions.z/2*simpleRef.scale.z))
    
    model.data.materials.append( bpy.data.materials.get(MODEL_SETUP_CONFIG["material"]) )
    model.active_material = bpy.data.materials.get(MODEL_SETUP_CONFIG["material"])
