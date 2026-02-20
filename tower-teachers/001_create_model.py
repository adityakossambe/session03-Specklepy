
## Step 1 : Create a new model in the specified project ##

from main import get_client
from specklepy.core.api.inputs.model_inputs import CreateModelInput

# Source project ID
PROJECT_ID = "128262a20c"  
# Model directory (will be created inside the project)
MODEL_NAME = "homework/session03/team_02.1_ad"

def main():
    # Authenticate
    client = get_client()

    # Create a basic model
    model = client.model.create(CreateModelInput(
    project_id=PROJECT_ID,
    name=MODEL_NAME,
    description="Session 03 homework for team 02.1",
    ))

    print(f"Created model: {model.name} (ID: {model.id})")


if __name__ == "__main__":
    main()
