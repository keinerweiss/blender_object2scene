# Render a model via commandline

## How to execute:

```
blender -b "/path/to/model_setup.blend" -P "/path/to/insert_model.py" -o "/path/to/my_output" -E BLENDER_EEVEE -F JPEG -f 1 -- "/path/to/model.dae"
```

![The result](/my_output0001.jpg)

## What does it do

1. Run in background, do not open a blender window
1. Open the base file "model_setup.blend".
	* This is the scene setup with lighting and shit
1. Run insert_model.py on th scene.
	* Inserts and positions the new model
1. Outputs to /path/to/my_output0001.jpg
1. Uses the Eevee engine to render (quick)
	* Can also be CYCLES (raytracing, slow)
1. Outputs jpg. Other formats possible
1. Will render the first frame
1. After "--" two strings can follow:
	1: model file
	1: scene file

## What the script does:

1. Read the configuration from the setup blend file
1. Remove everything that is not a mesh (one mesh expected) from the newly imported things
1. Create a bounding box around the object and link its properties to the model mesh
	* Location and Scale of the model is copied from the bounding box via Contraint
1. The bounding box is scaled and put in position according to the camera viewport best fit (from configuration)
1. Apply materials to ground and model

## Whats the configuration about?

```import mathutils

MODEL_SETUP_CONFIG = {

	# where the object should be placed
    "position": mathutils.Vector((0, 0, 0)),
	
	# the safe area to scale the object into
    "boundariesBox": mathutils.Vector((3, 3, 1.2)),
	
	# the material to apply to the newly added model (must be in the blend file already)
    "material": "ObjectSurface",
	
	# Objects to remove from the setup scene before import (usually demo mesh)
    "remove": ["Cylinder"],
	
	# Apply rigid body physics to the new object (not working yet)
    "physics": False
}```
