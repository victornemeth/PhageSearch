import mysql.connector

#######################################################
# Feature extraction out of ggf file
#######################################################
def parse_ggf3(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()

    species_info = {}
    current_species = None
    species_flag = False  # Flag to indicate the next line after ##species should be processed for nat_host name
    for line in data:
        if line.startswith('##species'):
            species_url = line.split()[1]
            current_species = species_url
            species_info[current_species] = {
                'Dbxref': None,
                'Lab-host': None,
                'Nat-host': None,
                'Old-name': None,
                'Proteins': []
            }
            species_flag = True
        elif species_flag:
            segments = line.split('\t')
            attributes = {attr.split('=')[0]: '='.join(attr.split('=')[1:]) for attr in segments[-1].split(';') if '=' in attr}
            species_info[current_species]["Dbxref"] = attributes.get('Dbxref')
            species_info[current_species]["Lab-host"] = attributes.get('lab-host')
            species_info[current_species]["Nat-host"] = attributes.get('nat-host')
            species_info[current_species]["Old-name"] = str(attributes.get('old-name')).replace("\n","")
            species_flag = False
        elif '\tCDS\t' in line:
            # Process CDS lines to extract protein information
            segments = line.split('\t')
            attributes = {attr.split('=')[0]: '='.join(attr.split('=')[1:]) for attr in segments[-1].split(';') if '=' in attr}
            protein_info = {
                'sequence-region' : segments[0],
                'CDS Start': segments[3],
                'CDS End': segments[4],
                'ID': attributes.get('ID'),
                'Dbxref': attributes.get('Dbxref'),
                'Note': attributes.get('Note'),
                'Product': attributes.get('product'),
                'Protein_id': attributes.get('protein_id')
            }
            species_info[current_species]['Proteins'].append(protein_info)

    return species_info

# Replace 'path_to_your_ggf3_file.ggf3' with the actual path to your .ggf3 file
file_path = 'gff_files/RefSeq_Phage_GFF3_File.gff3'
species_proteins_info = parse_ggf3(file_path)

# You can now access the extracted information as needed, for example:
# for species, info in species_proteins_info.items():
#     print(f"Species: {species}")
#     for protein in info['Proteins']:
#         print(f"\tProtein ID: {protein['ID']}, Product: {protein['Product']}")
print(species_proteins_info["https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=12417"])





#######################################################
# Connecting and exporting to mysql database
#######################################################
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    port = 3307,
    auth_plugin='mysql_native_password',
    database = "rbps_db"
)

mycursor = db.cursor()

# Helper function to insert a single species and return its primary key
def insert_species(species_data, cursor):
    cursor.execute("""
        INSERT INTO species (source, natural_host, lab_host, virus_name, dbxref)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        'RefSeq',  # Assuming 'RefSeq' is the source for all entries
        species_data['Nat-host'],
        species_data['Lab-host'],
        species_data['Old-name'],
        species_data['Dbxref']
    ))
    return cursor.lastrowid

# Helper function to insert proteins associated with a species
def insert_proteins(species_primary_key, proteins_data, cursor):
    for protein in proteins_data:
        cursor.execute("""
            INSERT INTO proteins (species_primary_key, source, seq_region, id, cds_start, cds_end, dbxref, note, product, protein_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            species_primary_key,
            'RefSeq',
            protein['sequence-region'],
            protein['ID'],
            protein['CDS Start'],
            protein['CDS End'],
            protein['Dbxref'],
            protein['Note'],
            protein['Product'],
            protein['Protein_id']
        ))

counter = 0
# Iterate over the parsed species and proteins and insert them into the database
for species, info in species_proteins_info.items():
    species_primary_key = insert_species(info, mycursor)
    insert_proteins(species_primary_key, info['Proteins'], mycursor)
    db.commit()  # Commit after each species is fully inserted
    print(counter)
    counter += 1

mycursor.execute("DELETE FROM proteins WHERE protein_id IS NULL;")
db.commit()  # Commit after each species is fully inserted
# Close the database connection
mycursor.close()
db.close()