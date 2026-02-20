
## Step 1 : Create a new model in the specified project ##

from main import get_client
from specklepy.objects import Base
from specklepy.core.api import operations
from specklepy.transports.server import ServerTransport
from specklepy.core.api.inputs.model_inputs import CreateModelInput
from specklepy.core.api.inputs.version_inputs import CreateVersionInput

# Source project ID
PROJECT_ID = "128262a20c"  
# Model directory (will be created inside the project)
MODEL_NAME = "homework/session04/team_02.1_ad"

def main():
    # Authenticate
    client = get_client()

    # Create a basic model
    model = client.model.create(CreateModelInput(
    project_id=PROJECT_ID,
    name=MODEL_NAME,
    description="Session 04 homework for team 02.1",
    ))
    print(f"Created model: {model.name} (ID: {model.id})")


    # Create empty root collection
    data = Base()
    data["name"] = "Random Box"
    data["elements"] = []
    print(f"✓ Created empty root collection for geometry data")
    
    transport = ServerTransport(client=client, stream_id=PROJECT_ID)
    obj_id = operations.send(base=data, transports=[transport])      

    version = client.version.create(CreateVersionInput(
        projectId=PROJECT_ID,
        modelId=model.id,
        objectId=obj_id,
        message="Sorted existing data into collections via specklepy"
    ))
    print(f"✓ Created version: {version.id}")
 

if __name__ == "__main__":
    main()
