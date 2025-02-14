from django.db import models

# Create your models here.


class Proteins(models.Model):
    primary_key = models.AutoField(primary_key=True)
    species_primary_key = models.ForeignKey('Species',on_delete = models.CASCADE, db_column='species_primary_key', blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    seq_region = models.CharField(max_length=50, blank=True, null=True)
    id = models.CharField(max_length=255, blank=True, null=True)
    cds_start = models.IntegerField(blank=True, null=True)
    cds_end = models.IntegerField(blank=True, null=True)
    dbxref = models.CharField(max_length=700, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    product = models.CharField(max_length=255, blank=True, null=True)
    protein_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proteins'


class Sequences(models.Model):
    primary_key = models.AutoField(primary_key=True)
    proteins_primary_key = models.ForeignKey(Proteins, on_delete = models.CASCADE, db_column='proteins_primary_key', blank=True, null=True, related_name='sequences_set')
    seq = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sequences'


class Species(models.Model):
    primary_key = models.AutoField(primary_key=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    natural_host = models.CharField(max_length=255, blank=True, null=True)
    lab_host = models.CharField(max_length=255, blank=True, null=True)
    virus_name = models.CharField(max_length=255, blank=True, null=True)
    dbxref = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'species'

class Structures(models.Model):
    primary_key = models.AutoField(primary_key=True)
    proteins_primary_key = models.ForeignKey(Proteins, on_delete = models.CASCADE, db_column='proteins_primary_key', blank=True, null=True, related_name='structures_set')
    pdb_id = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.CharField(max_length=255, blank=True, null=True)
    pdb_file = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'structures'