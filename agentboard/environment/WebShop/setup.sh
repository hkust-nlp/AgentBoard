#!/bin/bash

# Download spaCy large NLP model
python -m spacy download en_core_web_lg

# Build search engine index
cd search_engine
mkdir -p resources resources_100 resources_1k resources_100k
python convert_product_file_format.py # convert items.json => required doc format
mkdir -p indexes
./run_indexing.sh
cd ..

mkdir -p user_session_logs/
cd user_session_logs/
echo "Downloading example trajectories complete"
cd ..
