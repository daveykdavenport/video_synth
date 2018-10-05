import sys
import pyglet


#setup pyglet & the video
path = r"/Users/Davey/Python_Projects/Video_Synth/videos/guns2.mpg"
source = pyglet.media.load(path)

format = source.video_format
if not format:
    print('No video track in this source.')
    sys.exit(1)

player = pyglet.media.Player()
player.queue(source)
player.play()

window = pyglet.window.Window(width=format.width, height=format.height)

@window.event
def on_draw():
    player.get_texture().blit(0, 0)

    pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
    [0, 1, 2, 0, 2, 3],
    ('v2i', (100, 100,
             150, 100,
             150, 150,
             100, 150))
)

pyglet.app.run()
