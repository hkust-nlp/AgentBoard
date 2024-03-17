
if [ $INSTALL_WEBARENA = false ]; then
## Tool/game24/babyi/pddl
pip install -r requirements.txt

## jericho
#apt update
#apt install -y build-essential libffi-dev curl
#export CC=/usr/bin/gcc
#export CXX=/usr/bin/g++

pip install https://github.com/MarcCote/downward/archive/faster_replan.zip
pip install https://github.com/MarcCote/TextWorld/archive/handcoded_expert_integration.zip
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm
##

## alfworld
git clone https://github.com/leoozy/alfworld.git alfworld
cd alfworld
pip install -r requirements.txt
pip install .
cd ..
##

## Webshop
# Install Environment Dependencies via `conda`
conda install mkl=2021

conda install -c pytorch faiss-cpu

conda install -c conda-forge openjdk=11

# Build search engine index
cd ./agentboard/environment/WebShop/search_engine
mkdir -p resources resources_100 resources_1k resources_100k
python convert_product_file_format.py # convert items.json => required doc format
mkdir -p indexes
./run_indexing.sh
cd ../../../
##


else
## Webarena
  playwright install
  Xvfb :99 -screen 0 1280x720x24 &
  export DISPLAY=:99
fi
