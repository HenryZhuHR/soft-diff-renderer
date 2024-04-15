import os
import cv2
import torch
import tqdm
import numpy as np
import imageio
import argparse


import soft_renderer as sr
import neural_renderer as nr


class RenderParam:
    def __init__(
        self,
        distance: float = 2.732,
        elevation: int = 30,
        azimuth: int = 30,
        image_size: int = 256,
        texture_size: int = 2,
    ) -> None:
        self.distance = distance
        self.elevation = elevation
        self.azimuth = azimuth
        self.image_size = image_size
        self.texture_size = texture_size


def main():
    args = get_args()

    obj_file: str = args.filename_input
    out_dir: str = args.output_dir

    os.makedirs(out_dir, exist_ok=True)

    render_param = RenderParam(
        distance=2.732,
        elevation=30,
        azimuth=30,
        image_size=256,
        texture_size=4,
    )

    # render image
    ri_softRas = softRas_render(obj_file, render_param)
    cv2.imwrite(os.path.join(out_dir, "softRas.png"), ri_softRas)

    ri_nmr = nmr_render(obj_file, render_param)
    cv2.imwrite(os.path.join(out_dir, "nmr.png"), ri_nmr)
    
    ri_deodr = deodr_render(obj_file, render_param)
    cv2.imwrite(os.path.join(out_dir, "deodr.png"), ri_deodr)


def softRas_render(obj_file: str, rp: RenderParam):
    mesh_ = sr.Mesh.from_obj(
        obj_file, load_texture=True, texture_res=rp.texture_size, texture_type="surface"
    )

    # create renderer with SoftRas
    transform = sr.LookAt()
    lighting = sr.Lighting()
    rasterizer = sr.SoftRasterizer(image_size=rp.image_size)

    mesh = lighting(mesh_)
    transform.set_eyes_from_angles(rp.distance, rp.elevation, rp.azimuth)
    mesh = transform(mesh)

    images: torch.Tensor = rasterizer(mesh)[0]

    image: np.ndarray = images.detach().cpu().numpy()
    image = (255 * image.transpose((1, 2, 0))).astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image


def nmr_render(obj_file: str, rp: RenderParam):
    # load .obj
    vertices, faces, textures = nr.load_obj(
        obj_file, texture_size=rp.texture_size, load_texture=True
    )
    vertices = vertices[
        None, :, :
    ].cuda()  # [num_vertices, XYZ] -> [batch_size=1, num_vertices, XYZ]
    faces = faces[None, :, :].cuda()  # [num_faces, 3] -> [batch_size=1, num_faces, 3]
    textures = textures[None, :, :].cuda()

    renderer = nr.Renderer(camera_mode="look_at")
    renderer.eye = nr.get_points_from_angles(rp.distance, rp.elevation, rp.azimuth)
    images, _, _ = renderer.forward(vertices, faces, textures)
    images = images[0]
    image: np.ndarray = images.detach().cpu().numpy()
    image = (255 * image.transpose((1, 2, 0))).astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image


def deodr_render(obj_file: str, rp: RenderParam):
    pass


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--filename-input",
        type=str,
        default="data/spot/spot_triangulated.obj",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default="tmp",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
