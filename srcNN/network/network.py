import numpy as np
from activations import Relu
from activations import Linear
from dropout import DropNull
import random

class Network:
    """The code for this class is a modified version of that provided in Michael Nielsen's
    fantastic free book: http://neuralnetworksanddeeplearning.com
    """

    def __init__(self, weights, biases, activations, name='network', drop_scheme=DropNull()):
        """Create a neural network, specified by the layers which have varying sizes and activations"""
        self.num_layers = len(weights)+1
        self.weights = weights
        self.biases = biases
        self.activations = activations
        self.name = name
        self.drop_scheme = drop_scheme

    def feedforward(self, a):
        # Return the output of the network of 'a' is input
        for b, w, act in zip(self.biases, self.weights, self.activations):
            z = act.weighted_sum(w, b, a)
            a = act.apply(z)
        return a

    def feedforward_to(self, a, l):
        """Only feedforward to the layer l"""
        current_layer = 0;
        for b, w, act, in zip(self.biases, self.weights, self.activations):
            if current_layer == l:
                break
            z = act.weighted_sum(w, b, a)
            a = act.apply(z)
            current_layer += 1
        return a

    def update_mini_batch(self, mini_batch):
        self.drop_scheme.new_batch()
        """Update the network's weights and biases by applying
        gradient descent using backpropagation using a single mini batch.
        The 'mini_batch' is a list of tuples (x, y) and eta
        is the learning rate"""
        m = len(mini_batch)
        nabla_w, nabla_b, dzs = self.get_grads_for_mini_batch(mini_batch)
        nabla_w = self.drop_scheme.drop_grads(nabla_w)
        self.weights = [act.opt().update_weights(w, dw, m)
         for w, dw, act in zip(self.weights,nabla_w, self.activations)]
        self.biases = [act.opt().update_biases(b, db, m)
         for b, db, act in zip(self.biases, nabla_b, self.activations)]
        return nabla_w, nabla_b, dzs

    def get_grads_for_mini_batch(self, mini_batch):
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        dzs = []
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w, dz = self.backprop(x, y)
            nabla_b = [nb + dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw + dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
            dzs.append(dz)
        return nabla_w, nabla_b, dzs


    def backprop(self, x, y):
        """Return a tuple ``(nabla_b, nabla_w)`` representing the
        gradient for the cost function C_x.  ``nabla_b`` and
        ``nabla_w`` are layer-by-layer lists of numpy arrays, similar
        to ``self.biases`` and ``self.weights``."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        nabla_z = []
        # feedforward
        a = x
        a_values = [x]  # list to store all the activations, layer by layer
        weights = self.drop_scheme.drop_weights(self.weights)
        for b, w, act in zip(self.biases, weights, self.activations):
            z = act.weighted_sum(w, b, a)
            a = act.apply(z)
            a_values.append(a)

        # backward pass
        act = self.activations[-1]
        delta = self.cost_derivative(a, y)* act.prime(a_values[-1])
        nabla_z.append(delta)
        nabla_w[-1], nabla_b[-1] = act.weight_grad(delta, a_values[-2])
        for l in xrange(2, self.num_layers):
            act = self.activations[-l]
            ap = act.prime(a_values[-l])
            delta = np.matmul(weights[-l+1].transpose(), delta) * ap
            nabla_z.append(delta)
            nabla_w[-l], nabla_b[-l] = act.weight_grad(delta, a_values[-l - 1])
        nabla_z.reverse()
        return nabla_b, nabla_w, nabla_z

    def cost_derivative(self, a, y):
        """Return the vector of partial derivatives \partial C_x /
        \partial a for the output activations."""
        return a - y

    def cost(self, coord):
        x, y = coord
        a = self.feedforward(x)
        return 1 / 2.0 * np.linalg.norm(y - a) ** 2

    def cost_batch(self, batch):
        return sum([self.cost(coord) for coord in batch])

    def half_weights(self):
        self.drop_scheme.half_weights(self.weights)

    def double_weights(self):
        self.drop_scheme.double_weights(self.weights)

