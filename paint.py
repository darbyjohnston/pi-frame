import argparse
import json
import os
import random
import sys
import PIL.Image
import PIL.ImageDraw
import PIL.ImageEnhance
import PIL.ImageFont

# Options.
rotate      = 0 # Possible values: 0, 90, 180, 270
brightness  = 1.2
contrast    = 1.2
font_path   = "NotoSans-Regular.otf"
font_size   = 18
retries     = 10

def layout_image_and_label(board_resolution, image_pos, image_resize, label_pos):
    if image_aspect > board_aspect:
        w = board_resolution[0]
        h = int(w / image_aspect)
        y = int(board_resolution[1] / 2 - h / 2)
        if y >= label_size[1]:
            # Special case: image is landscape and label fits in the letter box
            image_pos[1] = y
            image_resize[0] = w
            image_resize[1] = h
            label_pos[0] = board_resolution[0] / 2 - label_size[0] / 2
            if label_pos[0] < label_border:
                label_pos[0] = label_border
            label_pos[1] = y + h + label_border
    else:
        h = board_resolution[1]
        w = int(h * image_aspect)
        x = int(board_resolution[0] / 2 - w / 2)
        if x >= label_size[0]:
            # Special case: image is portrait and label fits in the letter box
            image_pos[0] = x
            image_resize[0] = w
            image_resize[1] = h
            label_pos[0] = image_pos[0] - label_size[0] + label_border
            label_pos[1] = board_resolution[1] - label_size[1] + label_border
    if not image_resize[0] or not image_resize[1]:
        available_height = int(board_resolution[1] - label_size[1])
        tmp_aspect = board_resolution[0] / float(available_height)
        if image_aspect > tmp_aspect:
            image_resize[0] = board_resolution[0]
            image_resize[1] = int(image_resize[0] / image_aspect)
            image_pos[1] = int(available_height / 2 - image_resize[1] / 2)
            label_pos[0] = board_resolution[0] / 2 - label_size[0] / 2
            if label_pos[0] < label_border:
                label_pos[0] = label_border
            label_pos[1] = image_pos[1] + image_resize[1] + label_border
        else:
            image_resize[1] = available_height
            image_resize[0] = int(image_resize[1] * image_aspect)
            image_pos[0] = int(board_resolution[0] / 2 - image_resize[0] / 2)
            label_pos[0] = board_resolution[0] / 2 - label_size[0] / 2
            if label_pos[0] < label_border:
                label_pos[0] = label_border
            label_pos[1] = image_pos[1] + image_resize[1] + label_border

# Parse command-line.
project_path = os.path.dirname(sys.argv[0])
parser = argparse.ArgumentParser(
    prog='painting',
    description='Display a random painting on an Inky Impression display')
parser.add_argument('collection')
parser.add_argument('-id')
args = parser.parse_args()

# Setup paths.
collection_path = args.collection
collection_dir = os.path.dirname(collection_path)

# Initialize the inky board.
board = None
board_resolution = [0, 0]
try:
    import inky
    board = inky.auto(ask_user=True, verbose=True)
    board_resolution = board.resolution
except ImportError:
    board_resolution = [1600, 1200]
print("Board resolution: {}".format(board_resolution))
if 90 == rotate or 270 == rotate:
    board_resolution = [board_resolution[1], board_resolution[0]]
board_aspect = board_resolution[0] / float(board_resolution[1])

# Open the collection.
try:
    with open(collection_path) as f:
        collection_json = json.load(f)
except FileNotFoundError:
    print("Cannot open file:", collection_path)
    sys.exit(1)

# Get the object IDs.
ids = []
for id in collection_json['objectIDs']:
    ids.append(id)
if 0 == len(ids):
    print("ERROR: No IDs found")
    sys.exit(1)
print("Number of IDs:", len(ids))

for i in range(retries):
    
    # Get the object.
    if args.id:
        id = args.id
    else:
        id = ids[random.randrange(len(ids) - 1)]
    print("ID:", id)
    object_path = os.path.join(collection_dir, "{}.json".format(str(id)))
    try:
        with open(object_path) as f:
            object_json = json.load(f)
    except:
        print("Cannot open file:", object_path)
        continue

    # Get the image.
    image_path = os.path.join(collection_dir, "{}.jpg".format(str(id)))
    try:
        image = PIL.Image.open(image_path)
    except:
        print("Cannot open file:", image_path)
        continue
    
    print("Title:", object_json['title'])
    print("Artist:", object_json['artistDisplayName'])
    print("Date:", object_json['objectEndDate'])
    print("Image size: {}".format(image.size))
    image_aspect = image.size[0] / float(image.size[1])

    # Create the background image.
    bg = PIL.Image.new(mode="RGB", size=board_resolution, color = 'black')
    
    # Create the label.
    label_font = PIL.ImageFont.truetype(os.path.join(project_path, font_path), font_size)
    label_pos = [0, 0]
    label = format(object_json['title'])
    if object_json['artistDisplayName'] and object_json['objectEndDate']:
        label += "\n{}, {}".format(object_json['artistDisplayName'], object_json['objectEndDate'])
    elif object_json['artistDisplayName']:
        label += "\n{}".format(object_json['artistDisplayName'])
    elif object_json['objectEndDate']:
        label += "\n{}".format(object_json['objectEndDate'])
    label_draw = PIL.ImageDraw.Draw(bg)
    label_border = label_draw.textbbox([0, 0], " ", font = label_font)[3] / 2
    label_bbox = label_draw.multiline_textbbox(label_pos, label, font = label_font, align='center')
    label_size = [label_bbox[2] + label_border * 2, label_bbox[3] + label_border * 2]

    # Calculate the layout of the image and label.
    image_pos = [0, 0]
    image_resize = [0, 0]
    label_pos = [0, 0]
    layout_image_and_label(board_resolution, image_pos, image_resize, label_pos)
            
    # Resize and adjust the image.
    print("Resizing image...")
    image = image.resize(image_resize)
    if brightness > 1.0:
        print("Adjusting image brightness...")
        enhancer = PIL.ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
    if contrast > 1.0:
        print("Adjusting image contrast...")
        enhancer = PIL.ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)

    # Show the image.
    print("Showing image...")
    bg.paste(image, image_pos)
    label_draw.multiline_text(label_pos, label, font = label_font, fill = 'white', align='center')
    if 90 == rotate:
        bg = bg.transpose(PIL.Image.ROTATE_90)
    elif 180 == rotate:
        bg = bg.transpose(PIL.Image.ROTATE_180)
    elif 270 == rotate:
        bg = bg.transpose(PIL.Image.ROTATE_270)
    if board:
        board.set_image(bg)
        board.show()
    else:
        bg.show()

    break

