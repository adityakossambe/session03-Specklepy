
## Step 2 : Create random data and append to the model created in step 1 ##

import random
from main import get_client
from specklepy.objects import Base
from specklepy.api import operations
from specklepy.transports.server import ServerTransport
from specklepy.core.api.inputs.version_inputs import CreateVersionInput
# Geometry libraries
from specklepy.objects.primitive import Interval
from specklepy.objects.geometry import Box, Point, Vector, Plane 

# Source project ID
PROJECT_ID = "128262a20c"
# Source model ID (Given)
MODEL_ID = "49694ed9b9"

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

    # Set model units
    u = "mm"

    # Generate random coordinates for origin
    random_x = random.uniform(-500, 500)
    random_y = random.uniform(-500, 500)
    random_z = random.uniform(-500, 500)

    random_origin = Point(x=random_x, y=random_y, z=random_z, units=u)
    print(f"✓ Generated random origin point at ({random_x:.2f}, {random_y:.2f}, {random_z:.2f})")

    # Create base plane
    base_plane = Plane(
        origin= random_origin,
        normal= Vector(x=0, y=0, z=1, units=u),   
        xdir= Vector(x=1, y=0, z=0, units=u),
        ydir= Vector(x=0, y=1, z=0, units=u),
        units=u    
    )        
    print(f"✓ Created base plane at origin with normal vector pointing up")

    # Create a box geometry
    box = Box(
        basePlane=base_plane,
        xSize = Interval(start=-50, end=50),
        ySize = Interval(start=-50, end=50),
        zSize = Interval(start=-50, end=50),
        units=u
    )
    print(f"✓ Created box geometry with size 50x50x50 centered at base plane")

    # create empty collection to transfer copied geometry   

    data["elements"].append(box)
    
    # Send the modified data back to Speckle
    object_id = operations.send(data, [transport])
    print(f"✓ Sent object: {object_id}")

    # Create a new version in the target model with the modifications
    version = client.version.create(CreateVersionInput(
        projectId=PROJECT_ID,
        modelId=MODEL_ID,
        objectId=object_id,
        message="Sent random box geometry to the model",
    ))
    print(f"✓ Created version: {version.id}")

if __name__ == "__main__":
    main()
