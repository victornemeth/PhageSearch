import mysql.connector
from Bio import SeqIO
import os

# Connect to the MySQL database
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    port=3307,
    auth_plugin='mysql_native_password',
    database="rbps_db"
)

mycursor = db.cursor()

# Select all protein IDs from the proteins table
mycursor.execute("SELECT primary_key,source,seq_region,protein_id FROM proteins")

# Fetch all the results
ids = mycursor.fetchall()

def insert_sequence(protein_primary_key, sequence, cursor):
    cursor.execute("""
        INSERT INTO sequences (proteins_primary_key, seq)
        VALUES (%s, %s)
    """, (
       protein_primary_key,
       str(sequence)
    ))

counter = 0
# Print out the protein IDs
for primary_key, source,seq_region,protein_id in ids:
    print(counter)
    counter += 1
    file_path = './fasta_files/' + source +"/" + seq_region +"/" + protein_id.replace("\n","") + ".fasta"
    if os.path.exists(file_path):
        for seq_record in SeqIO.parse(file_path, "fasta"):
            Sequence = seq_record.seq
    else:
        Sequence = None
    insert_sequence(primary_key,Sequence,mycursor)
    db.commit()

# Close the cursor and the connection
mycursor.close()
db.close()
