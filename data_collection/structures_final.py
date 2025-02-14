import re
import mysql.connector
import requests

proteinkeys = dict()

def extract_uniprot_ids_from_fasta(fasta_file):
    uniprot_ids = []
    with open(fasta_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                match = re.search(r'\|([A-Z0-9]+)\|', line)
                if match:
                    uniprot_ids.append(match.group(1))
    return uniprot_ids

def fetch_uniprot_ids_from_db():
    """Fetch UniProt IDs from the 'proteins' table in the 'rbps' database."""
    uniprot_ids = []
    try:
        # Connect to the MySQL database
        db = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            port=3307,
            auth_plugin='mysql_native_password',
            database="rbps"
        )
        cursor = db.cursor()

        # Select the UniProt_Ref field from the proteins table
        cursor.execute("SELECT primary_key, UniProt_Ref FROM proteins")
        
        # Fetch all rows and extract UniProt IDs
        rows = cursor.fetchall()
        for row in rows:
            # Skip rows where UniProt_Ref is NULL
            if row[1] is not None:
                # Assuming each row contains a UniProt ID in the format "UniProtKB/TrEMBL:ID"
                uniprot_id = row[1].split(":")[-1]  # Extract the ID part after the colon
                uniprot_ids.append(uniprot_id)
                proteinkeys[uniprot_id] = row[0]

        cursor.close()
        db.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    return uniprot_ids

def fetch_pdb_id_and_line_with_lowest_resolution(uniprot_id):
    """Fetch the PDB ID and line with the lowest resolution from the UniProt entry for the given UniProt ID."""
    try:
        print(uniprot_id)
        # Construct the UniProt entry URL for the given UniProt ID
        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.txt"
        
        # Send GET request to the UniProt entry URL
        response = requests.get(url)
        
        # Check if request was successful
        if response.status_code == 200:
            # Split the response content into lines
            lines = response.text.split('\n')
            
            # Extract lines starting with "DR   PDB;"
            pdb_lines = [line.strip() for line in lines if line.startswith("DR   PDB;")]
            
            if pdb_lines:
                # Initialize variables to store the lowest resolution and corresponding PDB ID and line
                lowest_resolution = float('inf')
                lowest_resolution_pdb_id = None
                lowest_resolution_line = None
                
                # Iterate over each PDB line
                for line in pdb_lines:
                    # Extract PDB ID and resolution value from the line
                    fields = line.split(';')
                    pdb_id = fields[1].strip()
                    resolution_str = fields[3].strip().split(' ')[0]
                    if resolution_str == '-':  # Skip lines with invalid resolution value
                        continue
                    resolution = float(resolution_str)
                    
                    # Check if the current resolution is lower than the lowest resolution found so far
                    if resolution < lowest_resolution:
                        lowest_resolution = resolution
                        lowest_resolution_pdb_id = pdb_id
                        lowest_resolution_line = line
                
                return lowest_resolution_pdb_id, lowest_resolution_line
            else:
                print(f"No PDB lines found for UniProt ID {uniprot_id}")
                return None, None
        else:
            print(f"Failed to retrieve UniProt entry for {uniprot_id}, status code: {response.status_code}")
            return None, None
    except requests.RequestException as e:
        print(f"Error fetching UniProt entry for {uniprot_id}: {e}")
        return None, None

def fetch_structure_from_pdb(pdb_id):
    """Fetch the structure corresponding to the given PDB ID."""
    try:
        # Construct the URL for fetching PDB structure data
        url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
        
        # Send GET request to the PDB URL
        response = requests.get(url)
        
        # Check if request was successful
        if response.status_code == 200:
            # Return the structure data
            return response.text
        else:
            print(f"Failed to retrieve structure for PDB ID {pdb_id}, status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching structure for PDB ID {pdb_id}: {e}")
        return None

def insert_structure_into_database(proteins_primary_key,pdb_id,metadata, filename):
    """Insert the structure data into the MySQL database."""
    try:
        # Connect to the MySQL database
        db = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            port=3307,
            auth_plugin='mysql_native_password',
            database="rbps"
        )
        cursor = db.cursor()

        # Insert the structure data into the database
        sql = "INSERT INTO structures (proteins_primary_key, pdb_id,metadata,pdb_file) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (proteins_primary_key, pdb_id,metadata,filename))
        db.commit()

        print(f"Structure for PDB ID {pdb_id} inserted into the database.")
        
        cursor.close()
        db.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def main():

    # Path to the FASTA file
    fasta_file = 'uniprotkb_database_pdb_NOT_taxonomy_id_2024_03_27.fasta'

    # Fetch UniProt IDs from FASTA file and database
    fasta_uniprot_ids = extract_uniprot_ids_from_fasta(fasta_file)
    db_uniprot_ids = fetch_uniprot_ids_from_db()

    # Find UniProt IDs that appear in both lists
    common_uniprot_ids = set(fasta_uniprot_ids).intersection(db_uniprot_ids)
    print("UniProt IDs common to both FASTA file and database:")
    print(common_uniprot_ids)
    print(len(common_uniprot_ids))

    # Fetch the PDB ID and line with the lowest resolution for each common UniProt ID
    for uniprot_id in common_uniprot_ids:
        pdb_id, pdb_line = fetch_pdb_id_and_line_with_lowest_resolution(uniprot_id)

        if pdb_id and pdb_line:
            print(f"UniProt ID: {uniprot_id}, PDB ID: {pdb_id}, Line with lowest resolution:")
            metadata = pdb_line
            print(metadata)
            print(pdb_line)
            # Fetch structure for the PDB ID
            pdb_data = fetch_structure_from_pdb(pdb_id)

            if pdb_data:
            
                filename = "./pdb_files/" + pdb_id + '.pdb'
                
                # Save the data to a PDB file
                with open(filename, 'w') as file:
                    file.write(pdb_data)
                print(f'Data saved to {filename}')


            if pdb_data:
                # Insert structure into the database
                proteins_primary_key = proteinkeys[uniprot_id]
                insert_structure_into_database(proteins_primary_key,pdb_id,metadata, filename)
                print(proteins_primary_key,pdb_id,metadata, filename)
            else:
                print(f"No structure found for PDB ID {pdb_id}")
        else:
            print(f"No PDB lines found for UniProt ID {uniprot_id}")

if __name__ == "__main__":
    main()
