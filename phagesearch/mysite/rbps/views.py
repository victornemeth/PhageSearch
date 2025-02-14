from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.db.models import Q, Prefetch, Count, OuterRef, Subquery, Value
from .models import Species, Proteins, Sequences, Structures
from django.db.models.functions import Coalesce
import requests
import biotite.structure.io as bsio
from io import BytesIO
from zipfile import ZipFile
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from django.urls import resolve
from django.db.models.functions import Length
from django.db.models import CharField, Value as V
import csv
from django.shortcuts import render
from collections import defaultdict
import json

def home(request):
    # Retrieve all query parameters
    product_query = request.GET.get('product', '')
    host_query = request.GET.get('host', '')
    virus_query = request.GET.get('virus', '')
    source_query = request.GET.get('source', '')
    structure_query = request.GET.get('structure', '')
    notes_query = request.GET.get('notes', '')
    rows_request = request.GET.get('rows', '10')

    # Default to 10 rows, parse to integer
    try:
        rows = int(rows_request)
        if rows > 1000:
            rows = 10
    except ValueError:
        rows = 10  # Fallback if conversion fails

    # Initialize query filters
    query_filters = Q()

    # Check if any filter is set
    any_filter = any([product_query, host_query, virus_query, source_query, structure_query, notes_query])

    # Apply filters if any are provided
    if any_filter:
        if product_query:
            query_filters &= Q(product__icontains=product_query)
        if host_query:
            query_filters &= (Q(species_primary_key__natural_host__icontains=host_query) | 
                              Q(species_primary_key__lab_host__icontains=host_query))
        if virus_query:
            query_filters &= Q(species_primary_key__virus_name__icontains=virus_query)
        if source_query:
            query_filters &= Q(source__icontains=source_query)
        if notes_query:
            query_filters &= Q(note__icontains=notes_query)
        if structure_query == "Uniprot":
                # Include only entries that have a pdb_file
                query_filters &= Q(structures_set__pdb_file__isnull=False)
            
        elif structure_query in ["ALL", "No"]:
            # Create a subquery for sequences, annotated with their lengths
            sequences_with_length = Sequences.objects.filter(
                proteins_primary_key=OuterRef('pk')
            ).annotate(seq_length=Length('seq'))
            
            if structure_query == "ALL":
                # Include entries that have a pdb_file or sequences shorter than 400 characters
                query_filters &= (
                    Q(structures_set__pdb_file__isnull=False) |
                    Q(pk__in=Subquery(sequences_with_length.filter(seq_length__lt=400).values('proteins_primary_key')))
                )
            elif structure_query == "No":
                # Exclude entries that have a pdb_file and include only sequences longer than 400 characters
                query_filters &= (
                    Q(structures_set__pdb_file__isnull=True) &
                    Q(pk__in=Subquery(sequences_with_length.filter(seq_length__gt=400).values('proteins_primary_key')))
                )

    # Query the database
    proteins_query = Proteins.objects.filter(query_filters).distinct().select_related('species_primary_key').prefetch_related('sequences_set', 'structures_set').order_by('primary_key')

    # Apply pagination
    paginator = Paginator(proteins_query, rows)
    page_number = request.GET.get('page', 1)
    proteins = paginator.get_page(page_number)

    # Query total count only if filters are applied
    total_count = proteins.paginator.count #if any_filter else 1000  # Default to 100 or the actual count when filtered

    context = {
        'proteins': proteins,
        'product_query': product_query,
        'host_query': host_query,
        'virus_query': virus_query,
        'source_query': source_query,
        'structure_query': structure_query,
        'notes_query': notes_query,
        'rows': rows_request,
        'total_count': total_count
    }
    return render(request, "home.html", context)


def host_suggestions(request):
    query = request.GET.get('query', '')
    # Update host suggestions to include both natural_host and lab_host
    hosts = Species.objects.filter(Q(natural_host__icontains=query) | Q(lab_host__icontains=query)).values_list('natural_host', 'lab_host').distinct()
    hosts_list = set([item for sublist in hosts for item in sublist if item])  # Flatten list and remove None
    return JsonResponse(list(hosts_list), safe=False)  # Return a list of matching hosts

def esmfold_prediction(request, sequence_pk, download_pdb_esm=False):
    sequence = get_object_or_404(Sequences, pk=sequence_pk)
    protein = sequence.proteins_primary_key  # Access the related Protein object
    species = protein.species_primary_key
    esmfold = True
    ############## pdb_file from sql db ################

    ############## ESMFOLD ################
    structurerror = ""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
    data = sequence.seq
    if len(sequence.seq) < 400:
        try: 
            response = requests.post(url,headers=headers, data=data,verify=False)
            pdb_string = response.content.decode('utf-8')

            with open('predicted.pdb', 'w') as f:
                f.write(pdb_string)

            struct = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
            b_value = round(struct.b_factor.mean(), 4)
            metadata = "Stucture predicted by ESMFold v1"
            esmfold = True
        except:
            metadata = ""
            pdb_string = ""
            b_value = ""
            structurerror = "Structure is not available, could be due to sequence length (limit is 400)"
    else:
        metadata = ""
        pdb_string = ""
        b_value = ""
        structurerror = "Structure is not available, could be due to sequence length (limit is 400)"
    #######################################
    sequence_length = len(sequence.seq)

    if download_pdb_esm:
        # Set the content type and headers for the response to indicate a file attachment
        response = HttpResponse(pdb_string, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=' + protein.protein_id + "_esmfold.pdb"
        return response

    context = {
        'sequence': sequence,
        'protein': protein,  # Pass the related Protein to the template
        'species': species,  # Pass the related Protein to the template
        'pdb_string' : pdb_string,
        'b_value' : b_value,
        "structurerror": structurerror,
        'sequence_length': sequence_length,
        'metadata': metadata,
        'esmfold': esmfold

    }
    return render(request, 'sequence_detail.html', context)


def sequence_detail(request, sequence_pk, download_pdb=False):
    sequence = get_object_or_404(Sequences, pk=sequence_pk)
    protein = sequence.proteins_primary_key  # Access the related Protein object
    species = protein.species_primary_key
    esmfold = False
    ############## pdb_file from sql db ################
    structure = Structures.objects.filter(proteins_primary_key=protein).first()
    if structure != None:
        metadata = structure.metadata
        pdb_string = ""
        b_value = ""
        structurerror = ""
        with open(structure.pdb_file, 'r') as f:
            pdb_string = f.read()
    else:
        ############## ESMFOLD ################
        structurerror = ""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
        data = sequence.seq
        if len(sequence.seq) < 400:
            try: 
                response = requests.post(url,headers=headers, data=data,verify=False)
                pdb_string = response.content.decode('utf-8')

                with open('predicted.pdb', 'w') as f:
                    f.write(pdb_string)

                struct = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
                b_value = round(struct.b_factor.mean(), 4)
                metadata = "Stucture predicted by ESMFold v1"
                esmfold = True
            except:
                metadata = ""
                pdb_string = ""
                b_value = ""
                structurerror = "Structure is not available, could be due to sequence length (limit is 400)"
        else:
            metadata = ""
            pdb_string = ""
            b_value = ""
            structurerror = "Structure is not available, could be due to sequence length (limit is 400)"


        # if response.status_code == 200:
        #     pdb = response.text
        # else:
        #     print("Request failed with status code:", response.status_code)
        #     pdb = 'not available'


    #######################################
    sequence_length = len(sequence.seq)

    # Check if the request is for downloading the PDB file
    if download_pdb:
        # Set the content type and headers for the response to indicate a file attachment
        response = HttpResponse(pdb_string, content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=' + protein.protein_id + ".pdb"
        return response

    context = {
        'sequence': sequence,
        'protein': protein,  # Pass the related Protein to the template
        'species': species,  # Pass the related Protein to the template
        'pdb_string' : pdb_string,
        'b_value' : b_value,
        "structurerror": structurerror,
        'sequence_length': sequence_length,
        'metadata': metadata,
        'esmfold': esmfold

    }
    return render(request, 'sequence_detail.html', context)

def download_sequences(request):
    product_query = request.GET.get('product', '')
    host_query = request.GET.get('host', '')

    host_filter = Q(proteins_primary_key__species_primary_key__natural_host__icontains=host_query) | \
                  Q(proteins_primary_key__species_primary_key__lab_host__icontains=host_query)

    sequences = Sequences.objects.filter(
        Q(proteins_primary_key__product__icontains=product_query) & host_filter
    ).select_related('proteins_primary_key')

    fasta_lines = []

    for sequence in sequences:
        header = f">{sequence.proteins_primary_key.protein_id}\n"
        fasta_lines.append(header)
        fasta_lines.append(sequence.seq + "\n")

    fasta_content = "".join(fasta_lines)
    response = HttpResponse(fasta_content, content_type="text/plain")
    response['Content-Disposition'] = 'attachment; filename="sequences.fasta"'

    return response

def analysis(request):
     return render(request, 'analysis.html')


def protein_analysis(request):
    product = request.GET.get('product', '')

    # Query all unique bacteria names including both natural_host and lab_host if available
    all_bacteria = Species.objects.values_list('natural_host', 'lab_host').distinct()

    # Query proteins and annotate results by host name
    data = Proteins.objects.filter(product__icontains=product).values(
        'species_primary_key__natural_host', 'species_primary_key__lab_host'
    ).annotate(
        count=Count('primary_key')
    )

    # Convert queryset to dictionary
    counts_dict = {(entry['species_primary_key__natural_host'], entry['species_primary_key__lab_host']): entry['count'] for entry in data}

    # Create separate entries for natural host and lab host
    combined_data = []
    for bacteria in all_bacteria:
        natural_host = bacteria[0]
        lab_host = bacteria[1]
        natural_host_count = counts_dict.get((natural_host, None), 0)
        lab_host_count = counts_dict.get((None, lab_host), 0)
        if natural_host:
            combined_data.append({'host': natural_host, 'count': natural_host_count})
        if lab_host:
            combined_data.append({'host': lab_host, 'count': lab_host_count})

    # Sort combined data by count in descending order
    combined_data = sorted(combined_data, key=lambda x: x['count'], reverse=True)

    return JsonResponse(combined_data, safe=False)

def download_structures(request):
    product_query = request.GET.get('product', '')
    host_query = request.GET.get('host', '')
    host_query = request.GET.get('host', '')

    host_filter = Q(proteins_primary_key__species_primary_key__natural_host__icontains=host_query) | \
                  Q(proteins_primary_key__species_primary_key__lab_host__icontains=host_query)

    sequences = Sequences.objects.filter(
        Q(proteins_primary_key__product__icontains=product_query) & host_filter
    ).select_related('proteins_primary_key')

    # Create a zip file in memory
    in_memory_zip = BytesIO()
    with ZipFile(in_memory_zip, 'w') as zip_file:
        for sequence in sequences:
            response = requests.post("https://api.esmatlas.com/foldSequence/v1/pdb/", data=sequence.seq, verify=False)
            if response.status_code == 200:
                file_name = f"{sequence.proteins_primary_key.protein_id}.pdb"
                zip_file.writestr(file_name, response.text)
            else:
                print(f"Error fetching structure for {sequence.proteins_primary_key.protein_id}")

    # Prepare the zip file for download
    in_memory_zip.seek(0)  # Set the file pointer to the start of the zip file
    response = HttpResponse(in_memory_zip, content_type="application/zip")
    response['Content-Disposition'] = 'attachment; filename="structures.zip"'

    return response

def about(request):
     return render(request, 'about.html')

def overview(request):
    # # Step 1: Read species names from the CSV file
    # species_names = []
    # with open('species.csv', 'r') as file:
    #     reader = csv.reader(file)
    #     for row in reader:
    #         species_names.extend(row)

    # # Step 2: Fetch data and process it
    # species_data = Species.objects.all().prefetch_related('proteins_set')

    # species_protein_count = defaultdict(int)
    # for species_instance in species_data:
    #     for species_name in species_names:
    #         if (species_instance.natural_host and species_name.lower() in species_instance.natural_host.lower()) or \
    #                 (species_instance.lab_host and species_name.lower() in species_instance.lab_host.lower()):
    #             species_protein_count[species_name] += species_instance.proteins_set.count()

    # # If both hosts belong to the same species, increment the count only once
    # for species_instance in species_data:
    #     if species_instance.natural_host and species_instance.lab_host and \
    #             species_instance.natural_host.lower() == species_instance.lab_host.lower() and \
    #             species_instance.natural_host.lower() in species_names:
    #         species_protein_count[species_instance.natural_host.lower()] -= species_instance.proteins_set.count()

    # with open('species_protein_count.csv', 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(['species', 'Protein Count'])
    #     for species, count in species_protein_count.items():
    #         writer.writerow([species, count])

    # # Step 3: Pass data to the template

    genus_protein_count = defaultdict(int)
    species_protein_count = defaultdict(int)

    # Step 1: Read data from the CSV file and populate the genus_protein_count dictionary
    with open('genus_protein_count.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        # Skip the header row
        next(reader)
        for row in reader:
            genus_protein_count[row[0]] = int(row[1])

    # Step 1: Read data from the CSV file and populate the species_protein_count dictionary
    with open('species_protein_count.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        # Skip the header row
        next(reader)
        for row in reader:
            species_protein_count[row[0]] = int(row[1])

    context = {
        'genus_protein_count': json.dumps(genus_protein_count),
        'species_protein_count': json.dumps(species_protein_count),
    }

    # Step 4: Render the template
    return render(request, 'overview.html', context)
