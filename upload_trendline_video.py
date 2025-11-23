#!/usr/bin/env python3
"""Simple script to upload trendline tutorial video to TwelveLabs"""
import os
from twelvelabs import TwelveLabs

# Initialize client
client = TwelveLabs(api_key=os.getenv('TWELVELABS_API_KEY', 'tlk_2GCM2KT0APCJNY2N72JS32W0DEPE'))

# Video file path
video_file = "/Users/MarcoPolo/Downloads/trendline-tutorial.mp4"

# First, list existing indexes
print("Listing existing indexes...")
try:
    indexes = client.index.list()
    if indexes:
        print(f"Found {len(indexes)} existing indexes:")
        for idx in indexes:
            print(f"  - {idx.name} (ID: {idx.id})")
        index_id = indexes[0].id
        print(f"\nUsing index: {index_id}")
    else:
        # Create new index
        print("No indexes found. Creating new index...")
        index = client.index.create(
            name="trendline-tutorial-analysis",
            models=[
                {"name": "marengo2.7", "options": ["visual", "audio"]},
                {"name": "pegasus1.2", "options": ["visual", "audio"]}
            ]
        )
        index_id = index.id
        print(f"Created index: {index_id}")
except Exception as e:
    print(f"Error with index operations: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# Upload video
print(f"\nUploading {video_file}...")
try:
    task = client.task.create(index_id=index_id, file=video_file, language="en")
    print(f"Task created: {task.id}")

    # Monitor progress
    def on_task_update(task):
        print(f"  Status: {task.status}")

    print("Waiting for indexing to complete...")
    task.wait_for_done(callback=on_task_update)

    if task.status != "ready":
        raise RuntimeError(f"Indexing failed with status {task.status}")

    print(f"\n✓ Video uploaded successfully!")
    print(f"Video ID: {task.video_id}")

except Exception as e:
    print(f"Error uploading video: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
