import random
from PIL import Image, ImageOps, ImageTk, ImageDraw
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.filedialog import asksaveasfilename
import shutil
from pathlib import Path
from math import floor
from os import remove as os_remove

root = tk.Tk()

my_images = [Path('tr_assets/red.jpg'), Path('tr_assets/green.jpg'), Path('tr_assets/blue.jpg')]
global preview_created
global grout_created
preview_created = 0
grout_created = 0

######## INPUT ########

box_width=tk.IntVar()
box_height=tk.IntVar()
resolution=tk.StringVar()
status=tk.StringVar()

columns=tk.IntVar()
rows=tk.IntVar()

# diffuse dims
global tw_dif
global th_dif
# grout dims
global tw_gro
global th_gro

# image transforms
flip_90=tk.IntVar()
flip_180=tk.IntVar()
mirror_hor=tk.IntVar()
mirror_ver=tk.IntVar()
ts=[0,0,0,0]

# odds
# [flip_90_odds, flip_180_odds, mirror_hor_odds, mirror_ver_odds]
odds=[None]*4
odds[0]=tk.IntVar()
odds[1]=tk.IntVar()
odds[2]=tk.IntVar()
odds[3]=tk.IntVar()

# if 1 flip to vert
direction=tk.IntVar()

# dif=0/grout=1 
grout=tk.IntVar()
show_grout_bool=tk.IntVar()
grout_line_width=tk.IntVar()
grout_border_width=tk.IntVar()
grout_around=tk.IntVar()

# prefilled input
seed_num = tk.IntVar()
seed_num.set(random.randint(0,10000))

###
global files_dir
files_dir="/"

#######################

def choose_image(bw, bh):
    image = Image.open(my_images[random.randint(0,len(my_images)-1)])
    try:
        o1 = odds[0].get()
        o2 = odds[1].get()
        o3 = odds[2].get()
        o4 = odds[3].get()
    except Exception:
        status.set("Transformation probabilities must be numbers from 0-100.")
        return

    if o1 not in range(0,101) or o2 not in range(0,101) or o3 not in range(0,101) or o4 not in range(0,101):
        status.set("Transformation probabilities must be numbers from 0-100.")
        return

    t = [0,0,0]
    if random.random()*100 <= o1: # flip 90
        if ts[0]:
            t[0] = 1
    if random.random()*100 <= o2: # flip 180
        if ts[1]:    
            t[1] = 1
    if random.random()*100 <= o3: # mirror hor
        if ts[2]:
            t[2] = 1
    if random.random()*100 <= o4: # mirror vert (hor + 180)
        if ts[3]:
            t[1] = (t[1] + 1) % 2
            t[2] = (t[2] + 1) % 2

    image = image.rotate(t[0]*90+t[1]*180)
    if t[2]:
        image = ImageOps.mirror(image)

    return image.resize((bw, bh))

def generate_image(bw, bh, gw, gh):
    try:
        random.seed(seed_num.get())
    except Exception:
        status.set("Seed must be a number.")
        return

    final = Image.new('RGB', (gw,gh))

    starting_y = 0
    while starting_y < gh:

        starting_x = 0
        while starting_x < gw:
            x = choose_image(bw, bh) 
            if not x: return
            final.paste(choose_image(bw, bh), (starting_x, starting_y, starting_x+bw, starting_y+bh))
            starting_x+=bw

        starting_y+=bh

    tw, th = final.size

    if direction.get(): 
        final = final.rotate(90, expand=True)
        tw, th = th, tw
    final.save('preview.jpg')
    global preview_created
    preview_created=1
    resolution.set(f"{tw}x{th}")

    global tw_dif, th_dif
    tw_dif, th_dif = tw, th
    return (tw,th)

def generate_grout(bw, bh, cols, rows, gl, gb):

    if grout_around.get():
        tw = bw*cols + gl*(cols-1) + 2*gb
        th = bh*rows + gl*(rows-1) + 2*gb
    else:
        tw = bw*cols
        th = bh*rows

    grout_img = Image.new('RGBA', (tw, th), (255, 255, 255))
    draw = ImageDraw.Draw(grout_img)

    if grout_around.get():
        cur_y=bh+gb
        for _ in range(rows-1):
            draw.rectangle([(0, cur_y), (tw, cur_y+gl-1)], fill="black")
            cur_y+=bh+gl
        
        cur_x=bw+gb
        for _ in range(cols-1):
            draw.rectangle([(cur_x, 0), (cur_x+gl-1, th)], fill="black")
            cur_x+=bw+gl
    else:
        cur_y=bh
        for _ in range(rows-1):
            draw.rectangle([(0, cur_y-gl/2), (tw, cur_y+gl/2-1)], fill="black")
            print((0, cur_y-gl/2), (tw, cur_y+gl/2-1))
            cur_y+=bh
        
        cur_x=bw
        for _ in range(cols-1):
            draw.rectangle([(cur_x-gl/2, 0), (cur_x+gl/2-1, th)], fill="black")
            print((cur_x-gl/2, 0), (cur_x+gl/2-1, th))
            cur_x+=bw

    if gb:
        draw.rectangle([(0, 0), (tw, gb-1)], fill="black")
        draw.rectangle([(0, 0), (gb-1, th)], fill="black")
        draw.rectangle([(0, th), (tw, th-gb)], fill="black")
        draw.rectangle([(tw-gb, th), (tw, 0)], fill="black")

    if direction.get(): 
        grout_img = grout_img.rotate(90, expand=True)
        tw, th = th, tw
    grout_img.save('preview.png')  
    global grout_created
    grout_created=1
    resolution.set(f"{tw}x{th}") 

    global tw_gro, th_gro
    tw_gro, th_gro = tw, th
    return (tw,th)

def update_preview():
    status.set("")

    try:
        bw = box_width.get()
        bh = box_height.get()
        gw = bw*columns.get()
        gh = bh*rows.get()
    except Exception:
        status.set("Grid Options can't be empty.")
        return

    if not my_images:
        status.set("No files uploaded.")        
        return
    if gw and gh and bw and bh:

        res = generate_image(bw, bh, gw, gh)
        if not res: return
        if not grout.get() and show_grout_bool.get():
            show_grout_bool.set(0)
        new_img = ImageTk.PhotoImage(Image.open("preview.jpg").resize(get_preview_dims(res[0], res[1])))

        if grout.get():
            try:
                gl_width = grout_line_width.get()
            except Exception:
                status.set("Grout lines width can't be empty.")
                return
            if gl_width<0:
                status.set("Grout lines width can't be less than 0.")
                return
            try:
                gb_width = grout_border_width.get()
            except Exception:
                status.set("Grout border width can't be empty.")
                return
            if gb_width<0:
                status.set("Grout border width can't be less than 0.")
                return
            res = generate_grout(bw, bh, columns.get(), rows.get(), gl_width, gb_width)
            if grout.get() and show_grout_bool.get():
                new_img = ImageTk.PhotoImage(Image.open("preview.png").resize(get_preview_dims(res[0],res[1])))
        
        prev_image.configure(image=new_img)
        prev_image.image(new_img)
    else:
        status.set("Grid Options can't be 0.")

def get_preview_dims(gw,gh):
    if gh/gw >= 4/3:
        k=gh/800
    else:
        k=gw/600
    return (floor(gw/k), floor(gh/k))

def browse_files():
    status.set("")
    global files_dir
    filenames = filedialog.askopenfilenames(initialdir = Path(files_dir), title = "Select File(s)", filetypes = (("JPG","*.jpg"),("JPEG","*.jpeg"),("PNG","*.png"),("TIF","*.tif"),("BMP","*.bmp"),("all files","*.*")))

    if filenames:
        for filename in filenames:
            listbox.insert("end", filename)
            my_images.append(filename)
            up_img = Image.open(filename)
            up_width, up_height = up_img.size
            # if up_width != box_width.get() and box_width.get() != 0:
            #     status.set("Uploaded images have different resolutions.")
            box_width.set(up_width)
            box_height.set(up_height)

        files_dir=filenames[0]

def handle_keypress(key):
    item = listbox.curselection()
    if len(item) > 0:
        if key.keysym=="BackSpace":
            delete_item()
            return
        listbox.selection_clear(item[0])
        if key.keysym=="Up":
            listbox.selection_set(item[0]-1)
        elif key.keysym=="Down":
            listbox.selection_set(item[0]+1)

def delete_item():
    item = listbox.curselection()
    
    if len(item) > 0:
        i = item[0]
        my_images.pop(i)
        listbox.delete(item)
        status.set("")
        if listbox.size() < i+1 and i!=0:
            listbox.selection_set(i-1)
        else:
            listbox.selection_set(i)

def new_seed(): seed_num.set(random.randint(0,10000))

def save_as():
    global preview_created
    if preview_created:
        new_filename = asksaveasfilename(filetypes = [('JPG', '*.jpg')], defaultextension = '.jpg', title="Save Diffuse As")
        if new_filename:
                shutil.copyfile("preview.jpg", new_filename+"_diff.jpg")

    global grout_created
    if grout_created:
        new_filename = asksaveasfilename(filetypes = [('PNG', '*.png')], defaultextension = '.png', title="Save Grout As")
        if new_filename:
                shutil.copyfile("preview.png", new_filename+"_grout.png")

def show_grout():
    preview_file = "preview.jpg"
    if grout.get() and show_grout_bool.get():
        preview_file = "preview.png"
        tw, th = tw_gro, th_gro
    else:
        tw, th = tw_dif, th_dif

    resolution.set(f"{tw}x{th}")

    new_img = ImageTk.PhotoImage(Image.open(preview_file).resize(get_preview_dims(tw, th)))
    prev_image.configure(image=new_img)
    prev_image.image(new_img)

def checkbox_update1(): ts[0] = flip_90.get()
def checkbox_update2(): ts[1] = flip_180.get()
def checkbox_update3(): ts[2] = mirror_hor.get()
def checkbox_update4(): ts[3] = mirror_ver.get()

root.title("Texture Randomizer")
# generate window in center
window_width =1050
window_height = 970
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
# resizability
root.resizable(True, True)
root.minsize(window_width, window_height)
# table
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)
# opacity
root.attributes('-alpha',1)
# position depth
#root.attributes('-topmost', 1)
# icon
root.iconbitmap(Path('tr_assets/favicon.png'))
root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=Path('./tr_assets/favicon.png')))

############ PREVIEW ############
#preview frame
prev_frame = tk.LabelFrame(root, text="PREVIEW", font=("arial", 25))
prev_frame.grid(column=1, row=0, sticky="NW", ipadx=0)

# preview image load
try:
    img_fd = Image.open("preview.jpg")
    wh = get_preview_dims(img_fd.size[0], img_fd.size[1])
    img = ImageTk.PhotoImage(img_fd.resize(wh))
except FileNotFoundError:
    img = None

prev_image = ttk.Label(prev_frame, image = img)
prev_image.grid(column=0, row=0)

# resolution
tk.Label(prev_frame, textvariable=resolution, font=("arial", 16)).grid(column=0, row=1, sticky="")

# downloads
download_icon = tk.PhotoImage(file=Path('tr_assets/download.png'))
download_btn = ttk.Button(prev_frame,image=download_icon,text='Download',compound=tk.LEFT,command=save_as).grid(column=0, row=2, sticky="", ipadx=5, ipady=5)

# show grout
tk.Checkbutton(prev_frame, text='Show Grout', command=show_grout, variable=show_grout_bool, onvalue=1, offvalue=0).grid(column=0, row=3, sticky="")

ttk.Label(prev_frame, text="Note: The preview is rescaled so it could have some inacurracies, download the image to see the real output image.", font=("arial", 10)).grid(column=0, row=4, sticky="N")

############ OPTIONS ############
# Options Frame
option_frame = tk.LabelFrame(root, text="OPTIONS", font=("arial", 25))
option_frame.grid(column=0, row=0, sticky="NW", ipadx=0)

options_frame = ttk.Frame(option_frame)
options_frame.grid(column=0, row=0, sticky="NW")

############ FILE MANAGER ############

fm_frame = ttk.Frame(options_frame)
fm_frame.grid(column=0, row=0, sticky="", padx=10)

ttk.Label(fm_frame, text="Input Files:", font=("arial", 16)).grid(column=0, row=0, sticky="NW", ipady=5)

listbox = tk.Listbox(fm_frame, height=6, width=40, selectmode="SINGLE")
listbox.grid(column=0, row=1)
scrollbar = tk.Scrollbar(fm_frame)
scrollbar.grid(column=1, row=1)
listbox.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = listbox.yview)

listbox.insert("end", "red.jpg")
listbox.insert("end", "green.jpg")
listbox.insert("end", "blue.jpg")

lb_frame = ttk.Frame(options_frame)
lb_frame.grid(column=0, row=1, sticky="N")

btn_explore = ttk.Button(lb_frame, text = "Browse Files", command = browse_files).grid(column=0, row=0, ipadx=3, ipady=3, sticky="NE")
btn_delete = ttk.Button(lb_frame, text = "Delete", command = delete_item).grid(column=1, row=0, ipadx=3, ipady=3, sticky="NW")
ttk.Label(options_frame, text="All input files should be the same resolution.", font=("arial", 10)).grid(column=0, row=2, sticky="N")


############ BOX FRAME ############

box_frame = ttk.Frame(options_frame)
box_frame.grid(column=0, row=3, sticky="W", ipady=10, padx=10)

ttk.Label(box_frame, text="Grid Options:", font=("arial", 16)).grid(column=0, row=0, sticky="NW", ipady=5)

#fetch box width 
tk.Label(box_frame, text="Box Width (px):", font=("arial", 13), bg="#ECECEC",).grid(column=0, row=1, sticky="E")
ttk.Entry(box_frame, textvariable=box_width).grid(column=1, row=1)

# fetch box height
tk.Label(box_frame, text="Box Height (px):", font=("arial", 13), bg="#ECECEC",).grid(column=0, row=2, sticky="E")
ttk.Entry(box_frame, textvariable=box_height).grid(column=1, row=2)

# fetch columns
tk.Label(box_frame, text="Columns:", font=("arial", 13), bg="#ECECEC",).grid(column=0, row=3, sticky="E")
ttk.Entry(box_frame, textvariable=columns).grid(column=1, row=3)

# fetch rows
tk.Label(box_frame, text="Rows:", font=("arial", 13), bg="#ECECEC",).grid(column=0, row=4, sticky="E")
ttk.Entry(box_frame, textvariable=rows).grid(column=1, row=4)

# resolution
tk.Label(box_frame, text="Resolution:", font=("arial", 13), bg="#ECECEC",).grid(column=0, row=5, sticky="E")
tk.Label(box_frame, textvariable=resolution, font=("arial", 13), bg="#ECECEC",).grid(column=1, row=5, sticky="W")

############ CHECKBOXES ############

check_frame = ttk.Frame(options_frame)
check_frame.grid(column=0, row=4, sticky="W", padx=10)
check_frame.columnconfigure(0, weight=1)
check_frame.columnconfigure(1, weight=2)

ttk.Label(check_frame, text="Image Transformation Options:", font=("arial", 16)).grid(column=0, row=0, ipady=5)
tk.Checkbutton(check_frame, text='Flip 90˚', font=("arial", 13), bg="#ECECEC", command=checkbox_update1, variable=flip_90, onvalue=1, offvalue=0).grid(column=0, row=1, sticky="W")
ttk.Entry(check_frame, textvariable=odds[0], width=3).grid(column=1, row=1)
tk.Checkbutton(check_frame, text='Flip 180˚', font=("arial", 13), bg="#ECECEC", command=checkbox_update2, variable=flip_180, onvalue=1, offvalue=0).grid(column=0, row=2, sticky="W")
ttk.Entry(check_frame, textvariable=odds[1], width=3).grid(column=1, row=2)
tk.Checkbutton(check_frame, text='Mirror Horizontally', font=("arial", 13), bg="#ECECEC", command=checkbox_update3, variable=mirror_hor, onvalue=1, offvalue=0).grid(column=0, row=3, sticky="W")
ttk.Entry(check_frame, textvariable=odds[2], width=3).grid(column=1, row=3)
tk.Checkbutton(check_frame, text='Mirror Vertically', font=("arial", 13), bg="#ECECEC", command=checkbox_update4, variable=mirror_ver, onvalue=1, offvalue=0).grid(column=0, row=4, sticky="W")
ttk.Entry(check_frame, textvariable=odds[3], width=3).grid(column=1, row=4)

ttk.Label(options_frame, text="The input box is for the probability of the transformation (0-100)", font=("arial", 10)).grid(column=0, row=5, sticky="NW", padx=10, ipady=10)
odds[0].set(50)
odds[1].set(50)
odds[2].set(50)
odds[3].set(50)

############ DIRECTION RADIO ############

radio_frame = ttk.Frame(options_frame)
radio_frame.grid(column=0, row=6, sticky="W", ipady=10, padx=10)

ttk.Label(radio_frame, text="Direction:", font=("arial", 16)).grid(column=0, row=0, sticky="NW", ipady=5)
tk.Radiobutton(radio_frame, text="Horizontal", value=0, variable=direction, font=("arial", 13), bg="#ECECEC",).grid(column=0, row=1, sticky="W")
tk.Radiobutton(radio_frame, text="Vertical", value=1, variable=direction, font=("arial", 13), bg="#ECECEC",).grid(column=0, row=2, sticky="W")

############ GROUT RADIO ############

grout_frame = ttk.Frame(options_frame)
grout_frame.grid(column=0, row=7, sticky="W", ipady=10, padx=10)

ttk.Label(grout_frame, text="Grout Options:", font=("arial", 16)).grid(column=0, row=0, sticky="NW", ipady=5)
tk.Checkbutton(grout_frame, text='Create Grout', variable=grout, font=("arial", 16), bg="black", fg="white", onvalue=1, offvalue=0).grid(column=0, row=1, sticky="W")
tk.Label(grout_frame, text="Grout Lines width (px):", font=("arial", 13), bg="#ECECEC",).grid(column=0, row=2, sticky="NW", padx=5,  pady=2)
ttk.Entry(grout_frame, textvariable=grout_line_width, width=10).grid(column=0, row=2, padx=160)
tk.Label(grout_frame, text="Grout Border width (px):", font=("arial", 13), bg="#ECECEC",).grid(column=0, row=3, sticky="NW", padx=5,  pady=2)
ttk.Entry(grout_frame, textvariable=grout_border_width, width=10).grid(column=0, row=3, padx=160)
ttk.Checkbutton(grout_frame, text='Space Around (instead of superposed)', variable=grout_around, onvalue=1, offvalue=0).grid(column=0, row=4, sticky="W")
grout_line_width.set(2)
grout_border_width.set(1)


############ SEED ############

seed_frame = ttk.Frame(options_frame)
seed_frame.grid(column=0, row=8, sticky="W", ipady=10, padx=10)

ttk.Label(seed_frame, text="Seed:", font=("arial", 16)).grid(column=0, row=0, sticky="NW", ipady=5)
ttk.Entry(seed_frame, textvariable=seed_num).grid(column=0, row=1)
ttk.Button(seed_frame,text='Randomize',command= new_seed).grid(column=1, row=1, sticky="")

############ BUTTON ############
# generate
ttk.Button(options_frame,text='GENERATE', command = update_preview).grid(column=0, row=9, sticky="", ipadx=5, ipady=5)
tk.Label(options_frame, textvariable=status, font=("arial", 16), bg="#ECECEC", fg="orange").grid(column=0, row=10, sticky="S", ipady=5, ipadx=5, pady=10)

### KEYPRESS
root.bind("<KeyPress>", handle_keypress)

root.mainloop()

if preview_created: os_remove("preview.jpg")
if grout_created: os_remove("preview.png")

