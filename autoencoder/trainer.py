#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Aug 9, 2013

@author: Chunwei Yan @ pkusz
@mail:  yanchunwei@outlook.com
'''
from __future__ import division
import numpy as np
import layers
import noise

class Trainer():
    def train(self, layers, X, y, n_iters=1):
        rows = np.arange(X.shape[0])
        for iters in range(n_iters):
            np.random.shuffle(rows)
            for idx in rows:
                tmp = X[[idx]]
                for i in range(len(layers)):
                    tmp = layers[i].activate(tmp)
                grad = layers[-1].backwardPass(y[[idx]])
                for i in range(len(layers)-1, -1, -1):
                    grad = layers[i].update(grad)
        return layers
        
class StackedDA():
    def __init__(self, structure, alpha=0.01):
        self.alpha = alpha
        self.structure = structure
        self.Layers = []
        print "Call \"pre_train(n_iters)\""
        
    def __repr__(self):
        return "\nStacked Denoising Autoencoder Structure:\t%s"%(" -> ".join([str(x) for x in self.structure]))
        
    def pre_train(self, X, n_iters=1, rate=0.3):
        self.structure = np.concatenate([[X.shape[1]], self.structure])
        self.X = X
        trainer = Trainer()
        print "Pre-training: "#, self.__repr__()
        for i in range(len(self.structure) - 1):
            print "Layer: %dx%d"%( self.structure[i], self.structure[i+1])
            s1 = layers.SigmoidLayer(self.structure[i], self.structure[i+1], noise=noise.SaltAndPepper(rate))
            s2 = layers.SigmoidLayer(self.structure[i+1], self.X.shape[1])
            s1, s2 = trainer.train([s1, s2], self.X, self.X, n_iters)
            self.X = s1.activate(self.X)
            self.Layers.append(s1)
    
    def finalLayer(self, y, n_iters=1, learner_size=200):
        print "Final Layer"
        sigmoid = layers.SigmoidLayer(self.X.shape[1], learner_size, noise=noise.GaussianNoise(0.1))
        softmax = layers.SoftmaxLayer(learner_size, y.shape[1])
        trainer = Trainer()
        sigmoid, softmax = trainer.train([sigmoid, softmax], self.X, y, n_iters)
        self.Layers.append(sigmoid)
        self.Layers.append(softmax)
     
    def fine_tune(self, X, y, n_iters=1):
        print "Fine Tunning"
        trainer = Trainer()
        self.Layers = trainer.train(self.Layers, X, y, n_iters)
     
    def predict(self, X):
        #print self
        tmp = X
        for L in self.Layers:
            tmp = L.activate(tmp)
        return tmp
               
