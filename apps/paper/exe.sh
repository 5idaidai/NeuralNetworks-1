#!/bin/bash

set -e
set -x

PROJECT_ROOT=/home/chunwei/Lab/NeuralNetworks/apps/paper
DATA_ROOT=$PROJECT_ROOT/data
CLEAN_DATA_PATH=$DATA_ROOT/clean.sentences.txt
WORD2VEC_MODEL_PH=$DATA_ROOT/models/1.w2v

DATA_PH=${DATA_ROOT}/duc06/sent_raw

# clean the DUC data
clean_data()
{
    DUC_path=${DATA_ROOT}/DUC
    paths=`find \`pwd\` -name *.sent`
    cd $PROJECT_ROOT
    for path in $paths; do
        echo "cleaninng $path"
        topath=$path.clean
        cat $path |  ./clean_sentence.py > $topath
    done
}


train_word2vec()
{
    toroot=$DATA_ROOT/models
    topath=$WORD2VEC_MODEL_PH
    path_list=$DATA_ROOT/duc.path.list
    cd $DATA_ROOT/DUC
    find `pwd` -name *.sent.clean.tree > $path_list
    mkdir -p $toroot
    cd $PROJECT_ROOT
    cat $path_list | ./_word2vec.py $topath
}

_split_array()
{
    local n_total_parts=$1
    local i_mod_part=$2
    local content=$3
    echo $content | awk -v n_total_parts=$n_total_parts -v i_mod_part=$i_mod_part \
    '{
    for(i=1; i<=NF; i++)
        {
            if(i%n_total_parts == i_mod_part)
            {
                printf "%s ", $i;
            }
        }
    }'
}

gen_syntax_tree()
{
    topath=$DATA_ROOT/syntax_trees.txt
    path_list=$DATA_ROOT/duc.path.list
    cd $DATA_ROOT/DUC
    #cd $DATA_ROOT/test
    find `pwd` -name *.sent.clean > $path_list
    cd $PROJECT_ROOT/syntax_tree
    n_total_parts=$1
    n_total_parts=$n_total_parts-1
    for((i=0;i<=$n_total_parts;i++)); do
    {
        echo `_split_array $n_total_parts $i "\`cat $path_list\`"` | ./to_tree.py
    }&
    done&
    wait 
    echo "done"
}

train_parse_tree_autoencoder()
{
    path_list=$DATA_ROOT/duc.path.list
    cd $DATA_ROOT/DUC/duc07/sent_raw
    #cd $DATA_ROOT/DUC
    find `pwd` -name *.sent.clean.tree > $path_list
    cd $PROJECT_ROOT
    cat $path_list | ./parse_tree_autoencoder.py
}

stree_to_sentence_vec()
{
    path_list=$DATA_ROOT/duc.path.list
    bae_path=$DATA_ROOT/models/pta_full/0-9-0.725609.pk
    cd $DATA_ROOT/DUC/duc06/sent_raw
    #cd $DATA_ROOT/DUC
    find `pwd` -name *.sent.clean.tree > $path_list
    cd $PROJECT_ROOT
    cat $path_list | ./parse_tree_to_sentence_vec.py $WORD2VEC_MODEL_PH $bae_path
}

train_graph_tree_autoencoder()
{
    path_list=$DATA_ROOT/duc.path.list
    cd $DATA_ROOT/DUC/duc06/sent_raw
    #cd $DATA_ROOT/DUC
    find `pwd` -name *.sent.clean.tree.vec > $path_list
    cd $PROJECT_ROOT
    cat $path_list | ./graph_tree_autoencoder.py 
}

vector_to_validate_format()
{
    path_list=$DATA_ROOT/duc.path.list
    cd $DATA_ROOT/DUC/duc06/sent_raw
    #cd $DATA_ROOT/DUC
    find `pwd` -name *.sent > $path_list
    cd tools
    for path in `cat $path_list`; do
        ./vector_to_validate_format.py $path $path.clean.tree.vec $path.json $path.vec
    done
}




#clean_data
#train_word2vec
#gen_syntax_tree 4
train_parse_tree_autoencoder
#stree_to_sentence_vec
#train_graph_tree_autoencoder
