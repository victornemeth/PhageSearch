# PhageSearch

Welcome to **PhageSearch**, a repository containing the code necessary to recreate the **Phage Protein Search Engine**, available at [https://phagesearch.bionetic.org/](https://phagesearch.bionetic.org/).

## Overview
PhageSearch is a specialized search engine designed for researchers and bioinformaticians working with bacteriophage proteins. It enables efficient searching and analysis of host-specific phage protein sequences, providing insights into their functions and structures.

## Features
- **Fast and Efficient Search**: Quickly find host-specific phage proteins.
- **Comprehensive Dataset**: Built on curated databases to ensure high-quality search results.
- **User-Friendly Interface**: Intuitive UI for seamless navigation and analysis.
- **Customizable Queries**: Filter and refine searches based on specific attributes.
- **Fasta and Structure Download options**: Easy access to filtered results for processing into bioinformatics pipelines.

## Getting Started
To set up PhageSearch locally or on your server, follow these steps:

### Prerequisites
- Python 3.8+
- Django framework
- MySQL database
- Required Python dependencies (see `requirements.txt`)

### Required Python Packages

Below is a list of Python packages required to run the PhageSearch data collection:

- mysql-connector-python – To connect and interact with the MySQL database
- requests – For fetching data from external sources
- biopython – For handling sequence data and parsing biological file formats

## Deployment
For production deployment, configure:
- Nginx or Apache as a reverse proxy
- Database optimizations for large-scale querying

## Contributing
We welcome contributions! Feel free to submit issues, feature requests, or pull requests to improve PhageSearch.

## Contact
For questions or support, visit [PhageSearch](https://phagesearch.bionetic.org/) or contact me at `victor18nemeth@hotmail.com`.

Happy searching!

