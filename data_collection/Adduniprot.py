import re
import mysql.connector

# Establish database connection
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    port=3307,
    auth_plugin='mysql_native_password',
    database="rbps"
)
cursor = db.cursor()

# Fetch dbxref values
cursor.execute("SELECT primary_key, dbxref FROM proteins WHERE LOWER(dbxref) LIKE '%uniprot%'")
rows = cursor.fetchall()

# Regex to find UniProt references. Adjust the pattern as needed for your specific data format.
# This pattern looks for 'UniProtKB' followed by any character (non-greedy), and then either a comma or the end of the string.
pattern = re.compile(r'(UniProt\S+?:\S+?)(,|$)', re.IGNORECASE)

# Update UniProt_Ref column
update_query = "UPDATE proteins SET UniProt_Ref = %s WHERE primary_key = %s"
for primary_key, dbxref in rows:
    # Find all UniProt references in dbxref
    matches = pattern.findall(dbxref)
    if matches:
        # For simplicity, just take the first match and the first group (the actual reference, not the trailing comma/end)
        uniProt_ref = matches[0][0]  # [0] for the first match, [0] again for the first group in the match
        cursor.execute(update_query, (uniProt_ref, primary_key))

db.commit()
cursor.close()
db.close()
