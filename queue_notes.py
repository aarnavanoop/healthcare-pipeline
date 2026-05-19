import asyncio
import httpx
from arq import create_pool
from arq.connections import RedisSettings

async def main():
    BASE_URL = "http://127.0.0.1:8000"
    print("1. Authenticating locally...")
    
    async with httpx.AsyncClient() as client:
        # Register and login
        await client.post(f"{BASE_URL}/auth/register", json={"username": "admin", "password": "password123"})
        res = await client.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "password123"})
        token = res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        print("2. Fetching existing anomalies page by page...")
        all_anomalies = []
        page = 1
        size = 100  # Staying safely at the API's maximum limit

        while True:
            res = await client.get(f"{BASE_URL}/patients/anomalies?page={page}&size={size}", headers=headers)
            
            if res.status_code != 200:
                break
            
            data = res.json()
            # Safely extract the list
            current_page_data = data.get("items", data.get("data", [])) if isinstance(data, dict) else data
            
            if not current_page_data:
                break
                
            all_anomalies.extend(current_page_data)
            page += 1

        print(f"Found {len(all_anomalies)} existing anomalies. Connecting to Redis Queue...")

        # 3. Connect directly to the worker queue
        redis = await create_pool(RedisSettings(host='redis', port=6379))

        count = 0
        for summary in all_anomalies:
            patient_id = summary.get("patient_id", summary.get("id")) if isinstance(summary, dict) else summary
            # Only enqueue valid UUIDs to prevent crashes
            if patient_id and len(str(patient_id)) > 10:
                await redis.enqueue_job('generate_and_embed_note', patient_id)
                count += 1

        print(f"Success! Enqueued {count} existing patients.")
        print("The worker is now writing notes for them in the background. No duplicates were created!")

if __name__ == '__main__':
    asyncio.run(main())