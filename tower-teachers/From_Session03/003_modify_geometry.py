
## Step 3 : Offset the new object as per specified axis ##

import copy
from main import get_client
from specklepy.api import operations
from specklepy.objects.base import Base
from specklepy.transports.server import ServerTransport
from specklepy.core.api.inputs.version_inputs import CreateVersionInput

# Source project ID
PROJECT_ID = "128262a20c"
# Model ID (Created in step 1)
MODEL_ID = "f9f812034b"
# Object appliocationId  (Copied and created in step 2)
TARGET_APPLICATION_ID = "7b26f0af-2fb5-49b6-9486-403c3ae03082"
# Object offset distance (in mm)
OFFSET_Z = 16000.0

def find_object_by_application_id(obj, target_id: str):

    """ Recursively search for an object with the given applicationId. """

    if not isinstance(obj, Base):
        return None
    
    app_id = getattr(obj, "applicationId", None)
    if app_id == target_id:
        return obj
    
    # Search in child elements
    elements = getattr(obj, "@elements", None) or getattr(obj, "elements", [])
    for element in elements or []:
        found = find_object_by_application_id(element, target_id)
        if found:
            return found
    
    return None

def offset_mesh_vertices(mesh, offset_z: float):

    """ Offset mesh vertices in the Z direction. Vertices are stored as flat list: [x1, y1, z1, x2, y2, z2, ...] """

    if hasattr(mesh, "vertices") and mesh.vertices:
        new_vertices = []
        for i in range(0, len(mesh.vertices), 3):
            new_vertices.append(mesh.vertices[i] )                  # x 
            new_vertices.append(mesh.vertices[i + 1])               # y
            new_vertices.append(mesh.vertices[i + 2] + offset_z)    # z + offset
        mesh.vertices = new_vertices

def offset_geometry(obj, offset_z: float):

    """ Offset geometry in the Z direction for various geometry types. """

    # Handle displayValue (common in Revit objects)
    display_value = getattr(obj, "displayValue", None) or getattr(obj, "@displayValue", None)
    if display_value:
        display_value = copy.deepcopy(display_value)
        obj.displayValue = display_value

        if isinstance(display_value, list):
            for mesh in display_value:
                offset_mesh_vertices(mesh, offset_z)
        else:
            offset_mesh_vertices(display_value, offset_z)
    
    # Handle direct vertices (for Mesh objects)
    if hasattr(obj, "vertices") and obj.vertices:
        offset_mesh_vertices(obj, offset_z)
    
    # Handle base point / location
    if hasattr(obj, "basePoint"):
        bp = obj.basePoint
        if hasattr(bp, "z"):
            bp.z += offset_z
    
    if hasattr(obj, "location"):
        loc = obj.location
        if hasattr(loc, "z"):
            loc.z += offset_z


def main():
    # Authenticate
    client = get_client()

    # Get the latest version (commit)
    versions = client.version.get_versions(MODEL_ID, PROJECT_ID, limit=1)
    latest_version = versions.items[0]
    print(f"  Latest version: {latest_version.id}")
    print(f"  Message: {latest_version.message}")

    # Receive the data from Speckle
    transport = ServerTransport(client=client, stream_id=PROJECT_ID)
    data = operations.receive(latest_version.referenced_object, transport)

    # Locate the target object to be offset by applicationId
    target_obj = find_object_by_application_id(data, TARGET_APPLICATION_ID)
    
    # Offset geometry
    offset_geometry(target_obj, OFFSET_Z)
    print(f"✓ Created copy with Z offset of {OFFSET_Z}")
    
    # Send the modified data back to Speckle
    object_id = operations.send(data, [transport])
    print(f"✓ Sent object: {object_id}")

    # Create a new version in the target model with the modifications
    version = client.version.create(CreateVersionInput(
        projectId=PROJECT_ID,
        modelId=MODEL_ID,
        objectId=object_id,
        message="Moved geometry up by 16m in Z direction",
    ))
    print(f"✓ Created version: {version.id}")

if __name__ == "__main__":
    main()