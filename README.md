# py_texture_generetor

----------------------------------------------------

## Random Texture Generator

Desktop App that can generate randomized patterns and textures from input files by rotating and mirroring specific images in the grid, with many customization options as well as the possibility to also generate a pattern grid of tiles (grout) to match the texture. Written in `python` with `tkinter`.


## Index

- Demo
- Features/Options
- Installation


## Demo

## Features/Options

### File Upload:
You can upload as many files as needed, single or multiple at the time. For the best output make sure all files are the same size to avoid deformation.

### Grid Options:
The app generates a grid from your inputted images, and with **Box Width** and **Box Height** you can customize the resolution of each grid entry. Whereas with **Columns** and **Rows** you can customize how many grid slots you would like to have on each axis.
The final image will have the pixel size of: `Box Width * Columns` by `Box Height * Rows`.

It is advised to keep the box size resolution smaller or equal to the resolution of the smallest image.

### Image Transformation Options:
In the image transformation options you can select what kind of transformation you would like to be applied and their probability.

- **Flip 90˚**: Rotate the image 90 degrees counter clockwise
- **Flip 180˚**: Rotate the image 180 degrees
- **Mirror Horizontally**: Swap the pixels on the image from left to right
- **Mirror Vertically**: Swap the pixels on the image from up to down

The calculation uses probability and not frequency, so a 50% chance does not equate 50% appearance. If you would like a certain transformation to always happen then set the probability to 100. If you would like it to never happen, set it to 0 or uncheck it. 

### Direction:
Direction lets you rotate the whole grid by 90 degrees. This option can be used to save time instead of having swap widths and heights, and rows and columns. Or for non-square images, swap their resolution.

### Grout Options:
In the grout options you are given the choice to create a blank grid for the tiles, where the background is white and the outlines are black. **Grout Line Width** sets the width of the middle lines, **Grout Border Width** sets the width of the border grid.
The **Space Around** checkbox lets you decide whether you would like the black lines to be drawn on the grid items or around them, the difference is with **Space Around** checked, the resolution of the grout becomes larger as the lines are drawn around the grid items instead of superposed. 

**Example:** `box-width = 10`, `box-height = 10`, `columns = 2`, `rows = 2`, `grout line = 2px`, `grout border=1px`:

	- Regular grout resolution: 20 x 20
	- Space around grout resolution: 24 x 24 (20px for the grid items plus 1px for each side border, plus 2px for the line within.)

### Seed:
The seed is a number (1-10000) used to intialize a pseudorandom number generator. It could be used to work on previously generated images (if remembered). The seed will enhance user experience as making modification to other options will not randomize the grid. **Randomize** can a always be clicked to get a new random seed number.

### Format:
In the drop down menu right before the generate button you can select whether you want the compiled image to be a PNG or JPG. This is important if your input images have any opacity settings that you would like to maintain, or if you want to avoid anti aliasing.

### Preview:
On the preview side you can see the image that has been generated. There is also a checkbox **Show Grout** which will let you switch between viewing the compiled image and the generated grout.

### Download:
Once the download buttton is pressed a prompt will appear to save the generate image (diffuse). After saving it you will get a second prompt to save the grid outline (grout), if you chose to generate one.

## Installation

You will for need to install `python3`, `pip`/`pip3`, and `Pillow`/`PIL`.

Then just run `python3 coll.py`. Works on MacOS, Linux, and Windows.
