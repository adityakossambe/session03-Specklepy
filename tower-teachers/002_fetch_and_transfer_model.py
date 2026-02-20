
## Step 2 : Fetch model from given source and transfer geometry to newly created model ##

import copy
import uuid
from main import get_client
from specklepy.objects import Base
from specklepy.api import operations
from specklepy.transports.server import ServerTransport
from specklepy.core.api.inputs.version_inputs import CreateVersionInput

# Source project ID
PROJECT_ID = "128262a20c"
# Source model ID (Given)
SOURCE_MODEL_ID = "a1014e4b32"
# Target model ID (Created in step 1)
TARGET_MODEL_ID = "f9f812034b"
# Designer names to add in properties
DESIGNERS = ["Aditya Kossambe", "David Agudelo", "Zeynep Dursun"]

def main():
    # Authenticate    
    client = get_client() 

    # Get the latest version (commit)
    versions = client.version.get_versions(SOURCE_MODEL_ID, PROJECT_ID, limit=1)
    latest_version = versions.items[0]
    print(f"  Latest version: {latest_version.id}")
    print(f"  Message: {latest_version.message}")

    # Receive the data from Speckle
    transport = ServerTransport(client=client, stream_id=PROJECT_ID)
    data = operations.receive(latest_version.referenced_object, transport)
    
    # Add custom properties to the root object
    data["name"] = "Tower"
    data["speckle_type"] = "Base"    
    # data["editing_member"] = "Aditya" # if required

    # Add properties to collection level
    elements = getattr(data, "@elements", None) or getattr(data, "elements", [])
    for i, element in enumerate(elements or []):
        if isinstance(element, Base):
            element["name"] = "Old_Modules"
            element["speckle_type"] = "Base"
            # element["editing_member"] = "Aditya"  # if required
    
    print(f"✓ Added properties to {len(elements) if elements else 0} elements")

    # create empty collection to transfer copied geometry
    New_Modules = Base()
    New_Modules["name"] = "New_Modules"
    New_Modules["speckle_type"] = "Base" 
    New_Modules["elements"] = []   

    print(f"✓ Created new collection: {New_Modules['name']}")

    # Add list of designers
    designers_old = [DESIGNERS[0], DESIGNERS[2]]
    designers_new = [DESIGNERS[1]]    

    # Add properties to object level  
    objects = getattr(element, "@elements", None) or getattr(element, "elements", [])

    for i, obj in enumerate (objects or []):
        # Add properties to old_modules objects
        props = getattr(obj, "properties", None)
        if props:
            props["Module"] = f"{2*i+1:02d}"
            props["Designer"] = designers_old[i]  
            
        if i==0: 
            # Make deep copy of the object to be added to new_modules collection
            obj_copy = copy.deepcopy(obj)

            # clear application id and add new one to avoid conflicts
            obj_copy.id = None
            obj_copy.applicationId = str(uuid.uuid4())    

            # Add properties to new_modules objects
            obj_copy["properties"]["Module"] = "02" 
            obj_copy["properties"]["Designer"] = designers_new[0]               
            New_Modules["elements"].append(obj_copy)
    
    # Add New_Modules collection to root collection 
    if New_Modules not in elements:
        elements.append(New_Modules)      

    # Send the modified data back to Speckle
    object_id = operations.send(data, [transport])
    print(f"✓ Sent object: {object_id}")

    # Create a new version in the target model with the modifications
    version = client.version.create(CreateVersionInput(
        projectId=PROJECT_ID,
        modelId=TARGET_MODEL_ID,
        objectId=object_id,
        message="Sorted existing data into collections via specklepy"
    ))
    print(f"✓ Created version: {version.id}")

if __name__ == "__main__":
    main()
