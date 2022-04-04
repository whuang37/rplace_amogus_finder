import requests
from PIL import Image
import numpy as np
import sys
urls = [["https://hot-potato.reddit.com/media/canvas-images/1649033287902-0-f-DijGJ2Nx.png", "https://hot-potato.reddit.com/media/canvas-images/1649033287775-1-f-VorT1kc3.png"],
        ["https://hot-potato.reddit.com/media/canvas-images/1649033287991-2-f-xvohIvov.png", "https://hot-potato.reddit.com/media/canvas-images/1649033437746-3-f-GkkpQk1R.png"]]

COLOR_MAP = {1: "body",
             2: "eyes",
             0: "background"}

amogus_0 = [[0, 1, 1, 1],
            [1, 1, 2, 2],
            [1, 1, 1, 1],
            [0, 1, 1, 1],
            [0, 1, 0, 1]]

amogus_1 = [[0, 1, 1, 1],
            [1, 1, 2, 2],
            [1, 1, 1, 1],
            [0, 1, 0, 1]]

amogus_2 = [[0, 1, 1, 1],
            [0, 1, 2, 2],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [0, 1, 0, 1]]

def create_amogus_map(amogus):
    # create a list of coordinates to check for colors
    amogus = np.array(amogus)
    y_flip = np.flip(amogus, axis=1)
    x_flip = np.flip(amogus, axis=0)
    xy_flip = np.flip(amogus, axis=(0,1))
    amogi = {"no_flip": amogus,
             "y_flip": y_flip,
             "x_flip": x_flip,
             "xy_flip": xy_flip}


    # appends each color part to a specific list for easy iteration
    amogus_color_coords = {}
    for orientation, matrix in amogi.items():
        t = {"body": [],
            "eyes": [],
            "background":[]}
        h, w = matrix.shape

        for i in range(h):
            for j in range(w):
                t[COLOR_MAP[matrix[i][j]]].append((i, j))
        
        amogus_color_coords[orientation] = t
    return amogus_color_coords

def stitch_images(urls):
    w, h = 2000, 2000
    result = Image.new("RGB", (w, h))

    for i in range(len(urls)):
        for j in range(len(urls[i])):
            temp = Image.open(requests.get(urls[i][j], stream=True).raw).convert("RGBA")
            temp_w, temp_h = temp.size
            # stitch all the images together
            result.paste(im=temp, box=(temp_w * j, temp_h * i))
    
    return result

# r = stitch_images(urls)
# r.save("test.png")

def check_amogus(x, y, pix, m):
    c = {}
    background_colors = []
    # check to see if the body parts have the same color
    for body_name, body_part in m.items():
        for coords in body_part:
            # collect all background c olors
            if body_name == "background":
                rgba = pix[x+coords[1], y+coords[0]]
                background_colors.append(rgba)
                continue
            if not body_name in c:
                c[body_name] = pix[x+coords[1], y+coords[0]]
            else:
                if c[body_name] != pix[x+coords[1], y+coords[0]]:
                    return False

    # make sure background is different color
    for bg_c in background_colors:
        if (bg_c == c["eyes"]) or (bg_c == c["body"]):
            return False

    # make sure eyes and body colors are different
    if c["eyes"] == c["body"]:
        return False
    
    return True

def lighten_amogus(x, y, darken_map_pixel_data, m):
    coords = m["body"].copy() + m["eyes"].copy()

    for coord in coords:
        darken_map_pixel_data[(x+coord[1]) + (y+coord[0])*2000] = (255,255,255,0)
    
    return darken_map_pixel_data

def darken_background(darken_map_pixel_data, im):
    darken_map = Image.new("RGBA", (2000, 2000))
    darken_map.putdata(darken_map_pixel_data)
    darken_map.save("test4.png")
    im.paste(darken_map, box=None, mask=darken_map)

    return im

def find_amogus(im, amogus_maps):
    pix = im.load()
    w, h = im.size
    darken_map = Image.new("RGBA", (w,h))
    darken_map_pixel_data = list(darken_map.convert("RGBA").getdata())
    darken_map_pixel_data = [(0,0,0, 185) for _ in range(len(darken_map_pixel_data))]
    counter = 0
    n_amogus = 0
    found_map = {}
    for i in range(w):
        for j in range(h):
            found = 0
            counter += 1
            if counter % 10000 == 0:
                print(f"On Pixel ({i}, {j})")
            # go through all possible amoguses
            for a_map in amogus_maps:
                if (i + 4 > w-1) or (j + 5 > h-1):
                    continue
                # go through all possible orientations
                for orientation, a_map_orient in a_map.items():
                    if (check_amogus(i, j, pix, a_map_orient)):
                        found = 1
                        found_map = a_map_orient
                        break
                if (found == 1):
                    break
            
            if (found == 1):
                # save here
                print(f"Found Amogus at {i}, {j}")
                n_amogus += 1
                darken_map_pixel_data = lighten_amogus(i, j, darken_map_pixel_data, found_map)
                continue
    
    print(f"{n_amogus} Amogi Found")
    return darken_map_pixel_data

if __name__ == "__main__":
    amogus_maps = []
    for a in (amogus_0, amogus_1, amogus_2):
        amogus_maps.append(create_amogus_map(a))
    img = stitch_images(urls)

    im1 = img.crop((0, 850, 5, 855))
    im1.save("test3.png")
    darken_map_pixel_data = find_amogus(img, amogus_maps)
    final = darken_background(darken_map_pixel_data, img)
    final.save("final.png")