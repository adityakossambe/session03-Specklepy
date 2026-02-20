
## Step 3 : GQL subscription with speckle and export json when a new version is created through step 2 ##

import os
import json
import asyncio
from main import get_client  
from gql import gql, Client
from dotenv import load_dotenv
from gql.transport.websockets import WebsocketsTransport

# Load environment variables
load_dotenv()

SPECKLE_TOKEN = os.environ.get("SPECKLE_TOKEN")
PROJECT_ID = "128262a20c"
OBJECT_ID = "05bef649892016b3993570c1d91f5fd4"

# Define the subscription query
subscription_query = gql("""
    subscription ProjectVersionsUpdated($projectId: String!) {
        projectVersionsUpdated(id: $projectId) {
            id
            modelId
            type
            version {
                id
                message
                createdAt
            }
        }
    }
""")

def query_object_data_graphql(client, project_id: str, object_id: str) -> dict:
    """
    Query object data from Speckle using GraphQL API.
    
    Args:
        client: Authenticated SpeckleClient instance
        project_id: The Speckle project ID
        object_id: The Speckle object ID
    
    Returns:
        Dictionary containing the query result
    """
    query = gql("""
    query GetObjectDataJSON($objectId: String!, $projectId: String!) {
        project(id: $projectId) {
            object(id: $objectId) {
                id
                speckleType
                data
            }
        }
    }
    """)
    
    variables = {
        "projectId": project_id,
        "objectId": object_id
    }
    
    # Execute GraphQL query using the client's HTTP session
    result = client.httpclient.execute(query, variable_values=variables)
    return result

async def subscribe_to_project_updates():
    """
    Subscribe to project version updates using WebSocket
    """
    # Create WebSocket transport with authentication
    transport = WebsocketsTransport(
        url="wss://app.speckle.systems/graphql",
        init_payload={
            "Authorization": f"Bearer {SPECKLE_TOKEN}"
        }
    )
    
    # Authenticate with Speckle client
    speckle_client = get_client()
    print(f"✓ Authenticated with Speckle")

    # Create a GraphQL client
    gql_client = Client(
        transport=transport,
        fetch_schema_from_transport=False,
    )
    
    try:
        async with gql_client as session:
            print(f"✓ Connected to Speckle WebSocket")
            print(f"✓ Listening for updates on project: {PROJECT_ID}")
            print("Press Ctrl+C to stop\n")
            
            try:
                # Subscribe to the query
                async for result in session.subscribe(
                    subscription_query,
                    variable_values={"projectId": PROJECT_ID}
                ):
                    print("=" * 50)
                    print("✓ New Update Received!")
                    print("=" * 50)
                    
                    data = result.get("projectVersionsUpdated")
                    if data:
                        print(f"ID: {data.get('id')}")
                        print(f"Model ID: {data.get('modelId')}")
                        print(f"Type: {data.get('type')}")
                        
                        version = data.get('version')
                        if version:
                            print(f"\nVersion Details:")
                            print(f"  - Version ID: {version.get('id')}")
                            print(f"  - Message: {version.get('message')}")
                            print(f"  - Created At: {version.get('createdAt')}")                        
                        print("\n")
                        
                    # Execute GraphQL query
                    try:
                        graphql_result = query_object_data_graphql(speckle_client, PROJECT_ID, OBJECT_ID)
                        print(f"✓ GraphQL query executed successfully")
                    except Exception as e:
                        print(f"⚠ GraphQL query failed: {e}")
                        return
                    
                    # Prepare output data
                    output = {
                        "projectId": PROJECT_ID,
                        "objectId": OBJECT_ID,
                        "data": graphql_result["project"]["object"]["data"]
                    }
                    
                    # Save to JSON file in the same directory as this script
                    script_dir = os.path.dirname(os.path.abspath(__file__))

                    # Record version creation time for timestamp
                    version_time = version.get('createdAt')
                    # Remove invalid filename characters 
                    filename_time = version_time.replace(":", "-")

                    output_file = os.path.join(script_dir, f"object_data_{filename_time}.json")
                    
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(output, f, indent=2, default=str)
                    
                    print(f"✓ Saved object data to {output_file}")

            except asyncio.CancelledError:
                print("\n\n✓ Subscription cancelled")
                raise
            except KeyboardInterrupt:
                print("\n\n✓ Subscription stopped by user")
                raise
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Ensure transport is properly closed
        await transport.close()
        print("✓ Connection closed properly")

if __name__ == "__main__":
    # Run the subscription
    asyncio.run(subscribe_to_project_updates())
