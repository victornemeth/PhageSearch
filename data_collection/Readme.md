### Steps to recreate the mysql database

1. Create a mysql database (see main `docker-compose.yml` file)
2. CREATE database rbps;
3. Insert the `createdb.sql` file into the rbps database
4. Fetch the raw data from phageapi.deepomics.org using `FetchFastas.py` and `FetchGFF3.py`
5. Run `main.py`

Alternatively to `main.py` you could also run each of the following script individually


6. Run `FeatureCollect.py` of the wanted databases
7. Run `Adduniprot.py`
8. Run `getseq.py`
9. Run `structures_final.py`

