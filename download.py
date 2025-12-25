import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

# Options.
retries = 3
timeout = 15

# Get the collection.
collection_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects?departmentIds=11"
collection_path = "collection.json"
for i in range(retries):
    try:
        print("Downloading:", collection_url)
        urllib.request.urlretrieve(collection_url, collection_path)
    except:
        print("Cannot retrieve url:", collection_url)
        time.sleep(timeout)
        continue
collection_json = None
try:
    with open(collection_path) as f:
        collection_json = json.load(f)
except:
    print("Cannot open file:", collection_path)
    sys.exit(1)

# Get the IDs.
ids = []
for id in collection_json["objectIDs"]:
    ids.append(id)
if 0 == len(ids):
    print("No IDs found")
    sys.exit(1)
print("Number of IDs:", len(ids))

# Get the objects.
for id in ids:
    print("ID:", id)

    for i in range(retries):

        # Get the JSON.
        object_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects/" + str(id)
        object_path = os.path.join(".", "{}.json".format(str(id)))
        try:
            f = open(object_path)
            f.close()
        except FileNotFoundError:
            try:
                print("Downloading:", object_url)
                urllib.request.urlretrieve(object_url, object_path)
            except:
                print("Cannot retrieve url:", object_url)
                time.sleep(timeout)
                continue
        object_json = None
        try:
            with open(object_path) as f:
                object_json = json.load(f)
        except:
            print("Cannot open file", object_path)
            break

        # Get the image.
        image_url = object_json['primaryImage']
        image_extension = os.path.splitext(urllib.parse.urlparse(image_url).path)[1]
        # \bug
        image_url = image_url.replace(' ', '%20')
        if not image_url:
            print("No image found")
            break
        image_path = os.path.join(".", "{}{}".format(str(id), image_extension))
        try:
            f = open(image_path)
            f.close()
        except FileNotFoundError:
            try:
                print("Downloading:", image_url)
                urllib.request.urlretrieve(image_url, image_path)
                time.sleep(timeout)
            except:
                print("Cannot retrieve url:", image_url)
                time.sleep(timeout)
                continue

        # Print information.
        print("Title:", object_json['title'])
        print("Artist:", object_json['artistDisplayName'])
        print("Date:", object_json['objectEndDate'])
        
        break
    print("")

