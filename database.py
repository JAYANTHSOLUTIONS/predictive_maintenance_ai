import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Get these from your Supabase Settings -> API
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY") # Use Service Role for Backend

supabase: Client = create_client(url, key)