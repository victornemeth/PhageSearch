import requests
import os
import tarfile

# Directory where you want to save the GFF files
directory = "fasta_files"

# Check if the directory exists, and if not, create it
if not os.path.exists(directory):
    os.makedirs(directory)

FASTA_dict = {
    "Genbank Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/Genbank.tar.gz",
    "RefSeq Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/RefSeq.tar.gz",
    "DDBJ Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/DDBJ.tar.gz",
    "EMBL Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/EMBL.tar.gz",
    "PhagesDB Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/PhagesDB.tar.gz",
    "GPD Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/GPD.tar.gz",
    "GVD Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/GVD.tar.gz",
    "MGV Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/MGV.tar.gz",
    "TemPhD Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/TemPhD.tar.gz",
    "CHVD Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/CHVD.tar.gz",
    "IGVD Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/IGVD.tar.gz",
    "IMG_VR Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/IMG_VR.tar.gz",
    "GOV2 Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/GOV2.tar.gz",
    "STV Protein FASTA File": "https://phageapi.deepomics.org/fasta/phage_sequence/proteins/STV.tar.gz"
}


def download_file(url, filename):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Construct the path to save the file within the specified directory
        file_path = os.path.join(directory, filename)
        
        # Open the file in binary write mode and save the content to the file
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully: {file_path}")
        return file_path
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return None

def decompress_tar_gz(file_path, extract_path='.'):
    # Check if the specified file is a .tar.gz file
    if file_path.endswith('.tar.gz'):
        # Open the .tar.gz file
        with tarfile.open(file_path, 'r:gz') as tar:
            # Extract all the contents into the directory specified by extract_path
            tar.extractall(path=extract_path)
            print(f"Extracted {file_path} to {extract_path}")
        # Remove the .tar.gz file after extracting its contents
        os.remove(file_path)
        print(f"Removed archive file: {file_path}")

# Example usage
for filename, url in FASTA_dict.items():
    tar_gz_filename = filename.replace(" ", "_") + ".tar.gz"
    file_path = download_file(url, tar_gz_filename)
    if file_path:
        decompress_tar_gz(file_path, directory)