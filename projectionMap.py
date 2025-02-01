#!/usr/bin/env python
#
# It can be executed by selecting the menu option: 'Filters/Test/Split channels'
# or by writing the following lines in the Python console (that can be opened with the
# menu option 'Filters/Python-Fu/Console'):
# >>> image = gimp.image_list()[0]
# >>> layer = image.layers[0]
# >>> gimp.pdb.python_fu_test_split_channels(image, layer)

from gimpfu import *

def map_pixels(img, layer) :
    ''' Creates three layers with the RGB channels of the selected layer.
    
    Parameters:
    img : image The current image.
    layer : layer The layer of the image that is selected.
    '''
    # Indicates that the process has started.
    gimp.progress_init("Discolouring " + layer.name + "...")

    # Set up an undo group, so the operation will be undone in one step.
    pdb.gimp_image_undo_group_start(img)

    # Get the layer position.
    pos = 0;
    for i in range(len(img.layers)):
        if(img.layers[i] == layer):
            pos = i
            
    # Create the new layers.
    layerR = gimp.Layer(img, layer.name + " MAP", layer.width, layer.height, layer.type, layer.opacity, layer.mode)
    layerR.add_alpha()
    img.add_layer(layerR, pos)
    
    # Clear the new layers.
    pdb.gimp_edit_clear(layerR)
    layerR.flush()
    
    # Separate the channels.
    try:

        mask = layer.mask

        tile = layer.get_tile(False, 0, 0)
        tilew = tile.ewidth
        tileh = tile.eheight

        # Calculate the number of tiles.
        tn = int(layer.width / tilew)
        if(layer.width % tilew > 0):
            tn += 1
        tm = int(layer.height / tileh)
        if(layer.height % tileh > 0):
            tm += 1
       
        # how many rows / columns do we need to map
        mapcol = 0
        maprow = 0

        # Easiest to scan cols / rows separately

        colchk = [0] * int(layer.width)
        rowchk = [0] * int(layer.height)

        try:

          for i in range(tn):
            basex = (i*tilew)
            for j in range(tm):
                basey = (j*tileh)
        
                # Get the tiles.
                tile = layer.get_tile(False, j, i)
                tileM = mask.get_tile(False, j, i)
       
                if (tile):

                  # Iterate over the pixels of each tile.
                  for x in range(tile.ewidth):
                    for y in range(tile.eheight):
                      pixelM = tileM[x,y]
                      if pixelM == "\x00":
                          colchk[basex + x] = 1
                          rowchk[basey + y] = 1

          for i in range(int(layer.width)):
              if colchk[i] == 1:
                 mapcol += 1
          for i in range(int(layer.height)):
              if rowchk[i] == 1:
                 maprow += 1

          gimp.message("rows: {}  cols: {}".format(maprow, mapcol))

          doubleX = 1
          if layer.width > 4096:
              doubleX = 2


        except Exception as err:
           gimp.message("Error calculating map colors: " + str(err))


        # Iterate over the tiles.
        for i in range(tn):
            basex = (i*tilew)
            for j in range(tm):
                basey = (j*tileh)
                # Update the progress bar.
                gimp.progress_update(float(i*tm + j) / float(tn*tm))
        
                # Get the tiles.
                tile = layer.get_tile(False, j, i)
                tileR = layerR.get_tile(False, j, i)
                tileM = mask.get_tile(False, j, i)
       
                if (tile):

                  # Iterate over the pixels of each tile.
                  for x in range(tile.ewidth):
                    for y in range(tile.eheight):
                        # Get the pixel and separate his colors.
                        pixel = tile[x,y]
                        pixelM = tileM[x,y]

                        #if (rowchk[basey + y] == 1) and (colchk[basex + x] == 1):
                        #   pixelR = pixel[0] + "\x00\x00"
                        #else:
                        #   pixelR = pixel[0] + "\xFF\xFF"
                        ax = basex + x
                        ay = basey + y

                        ax /= doubleX
                        pixR = (ax >> 4) & 0xFF
                        pixG = ((ax & 0xF) | ((ay & 0xF00) >> 4))
                        pixB = (ay & 0xFF)

                        pixelR = chr(pixR) + chr(pixG) + chr(pixB)
                        if pixelM == "\x00":
                            pixelR += chr(255)
                        else:
                            pixelR += chr(0)
                        
                        # Save the value in the channel layers.
                        tileR[x,y] = pixelR

        # Update the new layers.
        layerR.flush()
        layerR.merge_shadow(True)
        layerR.update(0, 0, layerR.width, layerR.height)
        
    except Exception as err:
        gimp.message("Unexpected error: " + str(err))
    
    # Close the undo group.
    pdb.gimp_image_undo_group_end(img)
    
    # End progress.
    pdb.gimp_progress_end()

register(
    "python_fu_test_map_pixels",
    "Map Pixels",
    "Map unique colors to transparent pixels",
    "CDF",
    "Open source (BSD 3-clause license)",
    "2025",
    "<Image>/Filters/Test/Map Pixels",
    "RGB, RGB*",
    [],
    [],
    map_pixels)

main()
