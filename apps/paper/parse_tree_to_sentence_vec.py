#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on March 7, 2014

@author: Chunwei Yan @ PKU
@mail:  yanchunwei@outlook.com
'''
from __future__ import division
import sys
import numpy as np
sys.path.append('..')
sys.path.append('../../')
from paper import config as cg
from utils import obj_from_file
from models.recursive_autoencoder import BinaryAutoencoder
from _word2vec import Trainer as Word2Vec
from models.recursive_autoencoder.binary_tree_autoencoder import BinaryTree, BinaryTreeAutoencoder
from syntax_tree.parse_tree import SyntaxTreeParser
from exec_frame import BaseModel, ExecFrame
from parse_tree_autoencoder import ParseTreeAutoencoder


class Tree2Vec(ParseTreeAutoencoder):
    def __init__(self, word2vec, bae):
        ParseTreeAutoencoder.__init__(self, word2vec)
        # replace bae with saved model
        self.bta.bae = bae
        self.bae = bae

    def get_vec_from_stree(self, stree):
        '''
        :parameters:
            stree: string of tree
        '''
        parse_tree = self.create_tree(stree)
        bt = BinaryTree(parse_tree.root, self.bae)
        if bt.n_children < 5:
            print '!! skip tree: two less children'
            print '>\t', parse_tree
            return
        bt.forward_update_vec()
        sentence_vec =  bt.root.vector
        return sentence_vec




if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print 'cat stree_paths | ./cmd.py w2v_ph bae_ph'
        sys.exit(-1)
    stree_paths = sys.stdin.read().split()
    # args
    w2v_ph, bae_ph = args
    # load word2vec
    _word2vec = Word2Vec()
    _word2vec.model_fromfile(w2v_ph)
    # load bae
    bae = obj_from_file(bae_ph)
    tree2vec = Tree2Vec(_word2vec, bae)
    for path in stree_paths:
        output = []
        with open(path) as f:
            strees = f.readlines()
            for stree in strees:
                stree = stree.strip()
                #print 'parsing', stree
                sentence_vec = tree2vec.get_vec_from_stree(stree)
                if sentence_vec is not None:
                    str_vec = ' '.join([str(i) for i in sentence_vec])
                    c = str_vec + "\r"  + stree
                    output.append(c)
        topath = "%s.vec" % path

        print 'write res to', topath
        with open(topath, 'w') as f:
            f.write('\n'.join(output))
