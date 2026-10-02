def to_png(data, ofile, maxwidth=0, maxheight=0):
    """Renders the SVG markup in data to the PNG file ofile, on a light grey background, scaled down
    (keeping the aspect ratio) to fit maxwidth x maxheight when they are given."""
    # imported here: they need the native cairo / ImageMagick libraries, only for this conversion
    import cairosvg
    from wand.image import Image
    from wand.color import Color

    if isinstance(data, str):
        data = data.encode("utf-8")
    cairosvg.svg2png(bytestring=data, write_to=ofile)

    with Image(filename=ofile) as img:
        print("actual dims are " + str((img.width, img.height)))
        if maxwidth and maxheight and (img.width > maxwidth or img.height > maxheight):
            print("converting to " + str((maxwidth, maxheight)))
            img.transform(resize="%dx%d" % (maxwidth, maxheight))
        img.background_color = Color("#EEEEEE")
        img.alpha_channel = "remove"
        img.save(filename=ofile)
