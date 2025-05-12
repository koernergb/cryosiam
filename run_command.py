'''

Run the script with the following command:
# python tomogram_denoising_pyfile.py --input_path /path/to/your/tomograms --out_path /path/to/save/inverted_scaled_tomograms --output_denoised_path /path/to/save/denoised_tomograms --tomo_name tomogram_name.mrc --z_axis 50

'''

import argparse
import subprocess

parser = argparse.ArgumentParser(description='Wrapper to run tomogram_denoising_pyfile.py with default arguments')
parser.add_argument('--input', type=str, required=True, help='Input path for tomograms')
parser.add_argument('--output', type=str, required=True, help='Output path for inverted/scaled tomograms')
args = parser.parse_args()

input_path = args.input
out_path = args.output
output_denoised_path = './denoised'
tomo_name = 'example.mrc'
z_axis = 50

cmd = [
    'python', 'tomogram_denoising_pyfile.py',
    '--input_path', input_path,
    '--out_path', out_path,
    '--output_denoised_path', output_denoised_path,
    '--tomo_name', tomo_name,
    '--z_axis', str(z_axis)
]

subprocess.run(cmd, check=True)