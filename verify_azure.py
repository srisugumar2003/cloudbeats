import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

def verify_azure():
    load_dotenv()
    connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'music-container')

    if not connection_string or connection_string == "your_connection_string_here":
        print("[ERROR] AZURE_STORAGE_CONNECTION_STRING not set in .env")
        return

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        # Try to list blobs or get properties
        try:
            container_client.get_container_properties()
            print(f"[OK] Successfully connected to Azure Blob Storage!")
            print(f"[OK] Container '{container_name}' exists.")
        except Exception:
            print(f"[INFO] Container '{container_name}' does not exist. Attempting to create...")
            container_client.create_container()
            print(f"[OK] Container '{container_name}' created successfully.")
            
    except Exception as e:
        print(f"[ERROR] Failed to connect to Azure: {e}")

if __name__ == "__main__":
    verify_azure()

