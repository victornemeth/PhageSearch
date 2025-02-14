import requests
import os

# Directory where you want to save the GFF files
directory = "gff_files"

# Check if the directory exists, and if not, create it
if not os.path.exists(directory):
    os.makedirs(directory)

GFF3_dict = {"Genbank Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/Genbank.gff3",
             "RefSeq Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/RefSeq.gff3",
             "DDBJ Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/DDBJ.gff3",
             "EMBL Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/EMBL.gff3",
             "PhagesDB Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/PhagesDB.gff3",
             "GPD Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/GPD.gff3",
             "GVD Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/GVD.gff3",
             "MGV Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/MGV.gff3",
             "TemPhD Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/TemPhD.gff3",
             "CHVD Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/CHVD.gff3" ,
             "IGVD Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/IGVD.gff3",
             "IMG_VR Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/IMG_VR.gff3",
             "GOV2 Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/GOV2.gff3",
             "STV Phage GFF3 File" : "https://phageapi.deepomics.org/fasta/phage_sequence/phage_gff3/STV.gff3"
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
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


# Example usage
for filename, url in GFF3_dict.items():
    download_file(url, filename.replace(" ","_")+".gff3")
