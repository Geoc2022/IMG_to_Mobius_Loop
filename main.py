import sys
import argparse

try:
    import numpy as np
    from PIL import Image
    import matplotlib.pyplot as plt
    from math import cos, sin, tau
except ImportError as e:
    print(f"Please install the following modules: numpy, pillow, matplotlib")
    print(f"Error: {e}")
    sys.exit(1)


def mobius(u, v, band_size=0.5):
    def s1(u):
        return np.array([cos(u), sin(u), 0])
    def band(u, v):
        return v * np.array([0, cos(u), sin(u)]) + (1 - v) * np.array([0, -cos(u), -sin(u)])

    return s1((tau * u)) + (band(((tau * u) + (tau / 4)) / 2, v) * band_size)

class MobiusBand:
    def __init__(self, img, band_size_adj=0):
        if not img.lower().endswith('.jpg'):
            raise ValueError("The image must be a .jpg file")
        self.image = Image.open(img)
        self.image_size = self.image.size
        self.image_array = np.asarray(self.image) / 255.0

        self.band_size = (self.image_size[1] / self.image_size[0]) + band_size_adj

    def __call__(self, u, v):
        return mobius(u, v, self.band_size)

    def render(self, elev=25, azim=-45, perspective=0.8, zoom=2.2, image_shift=0, res_factor=1, transparent=False, save=True):
        u, v = np.linspace(image_shift, 1 + image_shift, self.image_size[0] // res_factor), np.linspace(0, 1, self.image_size[0] // res_factor)
        u, v = np.meshgrid(u, v)

        coords = np.array([self(u_i, v_j) for u_i, v_j in zip(u.flatten(), v.flatten())])
        x, y, z = coords[:, 0].reshape(u.shape), coords[:, 1].reshape(u.shape), coords[:, 2].reshape(u.shape)

        u_img = (u * (self.image_array.shape[1] - 1)).astype(int)
        v_img = (v * (self.image_array.shape[0] - 1)).astype(int)
        colors = self.image_array[v_img % self.image_array.shape[0], u_img % self.image_array.shape[1]]

        if transparent:
            brightness = np.mean(colors, axis=-1)
            alpha = (brightness * 0.9)
            alpha = np.clip(alpha, 0.2, 1.0)
            colors = np.dstack((colors, alpha))
        else:
            colors = np.clip(colors, 0, 1)

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')

        mobius_loop = ax.plot_surface(x, y, z, facecolors=colors, rstride=1, cstride=1, antialiased=True, shade=True)

        ax.view_init(elev=elev, azim=azim)

        max_range = np.array([x.max() - x.min(), y.max() - y.min(), z.max() - z.min()]).max()
        mid = lambda coord: (coord.max() + coord.min()) / 2
        mid_x, mid_y, mid_z = mid(x), mid(y), mid(z) 

        scale = perspective / zoom
        ax.set_xlim(mid_x - max_range * scale, mid_x + max_range * scale)
        ax.set_ylim(mid_y - max_range * scale, mid_y + max_range * scale)
        ax.set_zlim(mid_z - max_range * scale, mid_z + max_range * scale)

        ax.axis('off')
        plt.show()

        if save:
            plt.savefig('mobius_strip_render.png', transparent=True, dpi=400)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render a Mobius strip with an image texture.")
    parser.add_argument("image", type=str, help="Path to the image file.")
    parser.add_argument("--band_size_adj", type=float, default=0, help="Adjusts the size of the band.")
    parser.add_argument("--elev", type=float, default=25, help="Elevation angle for the 3D plot.")
    parser.add_argument("--azim", type=float, default=-45, help="Azimuth angle for the 3D plot.")
    parser.add_argument("--perspective", type=float, default=0.8, help="Perspective scaling factor.")
    parser.add_argument("--zoom", type=float, default=2.2, help="Zoom factor for the plot.")
    parser.add_argument("--image_shift", type=float, default=0, help="Shift factor for the image on the horizontal direction.")
    parser.add_argument("--res_factor", type=int, default=1, help="Resolution factor for the plot (Higher factor means lower output resolution).")
    parser.add_argument("--transparent", action="store_true", help="Make the image texture transparent based on brightness.")
    parser.add_argument("--save", action="store_true", help="Save the rendered image.")

    args = parser.parse_args()

    mobius_band = MobiusBand(args.image, band_size_adj=args.band_size_adj)
    mobius_band.render(elev=args.elev, azim=args.azim, perspective=args.perspective, zoom=args.zoom, image_shift=args.image_shift, res_factor=args.res_factor, transparent=args.transparent, save=args.save)

