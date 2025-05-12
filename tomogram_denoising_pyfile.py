# Before running this script, clone the CryoSiam-beta repository into your project's root directory:
# git clone https://github.com/frosinastojanovska/cryosiam_beta.git

# Then, run the script with the following command:
# python tomogram_denoising_pyfile.py --input_path /path/to/your/tomograms --out_path /path/to/save/inverted_scaled_tomograms --output_denoised_path /path/to/save/denoised_tomograms --tomo_name tomogram_name.mrc --z_axis 50

import argparse
import os
import mrcfile
import numpy as np
import urllib.request
import yaml
import sys
import matplotlib.pyplot as plt

def invert_tomogram(tomo):
    return tomo * -1

def scale_tomogram(tomo, percentile_lower=None, percentile_upper=None):
    if percentile_lower:
        min_val = np.percentile(tomo, percentile_lower)
    else:
        min_val = tomo.min()
    if percentile_upper:
        max_val = np.percentile(tomo, percentile_upper)
    else:
        max_val = tomo.max()
    tomo = (tomo - min_val) / (max_val - min_val)
    return np.clip(tomo, 0, 1)

def read_yaml(file_path):
    with open(file_path, "r") as stream:
        data = yaml.safe_load(stream)
    return data

def save_yaml(data, file_path):
    with open(file_path, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)

def read_tomogram(filename):
    with mrcfile.open(filename, permissive=True) as m:
        return m.data

def main():
    parser = argparse.ArgumentParser(description='Denoise cryo-ET tomograms')
    parser.add_argument('--input_path', type=str, required=True, help='Path to the folder with tomogram .mrc file(s)')
    parser.add_argument('--out_path', type=str, required=True, help='Path to save the inverted and scaled tomogram(s)')
    parser.add_argument('--output_denoised_path', type=str, required=True, help='Path to save the denoised tomogram(s)')
    parser.add_argument('--tomo_name', type=str, default=None, help='Name of the tomogram file to visualize (optional)')
    parser.add_argument('--z_axis', type=int, default=50, help='Z-axis slice to visualize (optional)')
    args = parser.parse_args()

    input_path = args.input_path
    out_path = args.out_path
    output_denoised_path = args.output_denoised_path
    tomo_name = args.tomo_name
    z_axis = args.z_axis

    lower_end_percentage = 0.1
    upper_end_percentage = 99.9

    os.makedirs(out_path, exist_ok=True)

    if os.path.isdir(input_path):
        os.makedirs(out_path, exist_ok=True)
        for tomo in os.listdir(input_path):
            if tomo.endswith(".mrc") or tomo.endswith(".rec"):
                with mrcfile.open(os.path.join(input_path, tomo), permissive=True) as m:
                    tomogram = m.data
                    voxel_size = m.voxel_size
                tomogram = invert_tomogram(tomogram)
                tomogram = scale_tomogram(tomogram, lower_end_percentage, upper_end_percentage)
                with mrcfile.new(os.path.join(out_path, tomo), overwrite=True) as m:
                    m.set_data(tomogram)
                    m.voxel_size = voxel_size
    else:
        with mrcfile.open(input_path, permissive=True) as m:
            tomogram = m.data
            voxel_size = m.voxel_size
        tomogram = invert_tomogram(tomogram)
        tomogram = scale_tomogram(tomogram, lower_end_percentage, upper_end_percentage)
        with mrcfile.new(out_path, overwrite=True) as m:
            m.set_data(tomogram)
            m.voxel_size = voxel_size
    del tomogram

    model_path = "https://www.dropbox.com/scl/fi/sxobvwa7k2ju54aimexhr/denoising_model.ckpt?rlkey=u2m4lv07rmfxmwcv6rf9uqaot&st=i12gjlxd&dl=0"
    urllib.request.urlretrieve(model_path, "model.ckpt")

    original_config_file = '/content/cryosiam_beta/cryosiam/apps/dense_simsiam_regression/config_test.yaml'
    d = read_yaml(original_config_file)
    d['data_folder'] = out_path
    d['log_folder'] = output_denoised_path
    d['prediction_folder'] = output_denoised_path
    d['trained_model'] = 'model.ckpt'
    d['test_files'] = None
    d['hyper_parameters']['batch_size']=20
    user_config_file = '/content/cryosiam_beta/cryosiam/apps/dense_simsiam_regression/config.yaml'
    save_yaml(d, user_config_file)

    sys.path.insert(1, "/content/cryosiam_beta")
    os.environ['PATH'] += '/content/cryosiam_beta'
    from cryosiam.apps.dense_simsiam_regression.predict import main as predict_main
    predict_main(user_config_file)

    # Visualization (optional)
    if tomo_name is not None:
        tomogram = read_tomogram(os.path.join(out_path, tomo_name))
        denoised_tomogram = read_tomogram(os.path.join(output_denoised_path, tomo_name))
        plt.figure(figsize = (10,10))
        plt.imshow(tomogram[z_axis] * -1, cmap='gray')
        plt.figure(figsize = (10,10))
        plt.imshow(denoised_tomogram[z_axis] * -1, cmap='gray')
        plt.show()

if __name__ == '__main__':
    main()