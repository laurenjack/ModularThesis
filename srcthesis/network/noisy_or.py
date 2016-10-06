#### Libraries
# Standard libraries
import random

#Third party libraries
import numpy as np

class NoisyOr(object):
    def __init__(self, sizes):
        """The list ``sizes`` contains the number of neurons in the
        respective layers of the network.  For example, if the list
        was [2, 3, 1] then it would be a three-layer network, with the
        first layer containing 2 neurons, the second layer 3 neurons,
        and the third layer 1 neuron.  The biases and weights for the
        network are initialized randomly, using a Gaussian
        distribution with mean 0, and variance 1.  Note that the first
        layer is assumed to be an input layer, and by convention we
        won't set any biases for those neurons, since biases are only
        ever used in computing the outputs from later layers."""
        self.num_layers = len(sizes)
        self.sizes = sizes
        """ A list of vectors, each of height y (2 vectors for the two
        non-input layers"""
        self.biases = [postive_normal((y, 1)) for y in sizes [1:]]
        #print self.biases
        """The second line of the expression below pairs the first layer
        of neurons outputs with the second layers inputs (i.e.) (2,3)
        and pair the second layers outputs with the third layers inputs
        i.e. (3,1). So there is a tuple for each layer of connections.Each
        tuple is used to construct a weights matrix for that layer of
        connections. The first is a 3x2 matrix, the second is a 1x3 matrix.
        The matrix is aligned such that the input layer is the number of rows
        and the output layer is the number of columns, so that the weights
        are correctly align with the biases and can therefore be applied to the
        activation function"""
        self.weights = [postive_normal((y, x))
                       for x, y in zip(sizes[:-1], sizes[1:])]
        self.zero_weights = [np.zeros(w.shape)
                             for w in self.weights]
        self.zero_biases = [np.zeros(b.shape)
                            for b in self.biases]

    def feedforward(self, a):
        # Return the output of the network of 'a' is input
        for b, w in zip(self.biases, self.weights):
            a = cont_or(np.dot(w, a) + b)
        return a



    def update_mini_batch(self, mini_batch, eta):
        """Update the network's weights and biases by applying
        gradient descent using backpropagation using a single mini batch.
        The 'mini_batch' is a list of tuples (x, y) and eta
        is the learning rate"""
        #A list of zeroed out vectors, corresponding to each bias vector
        #and its dimensions
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        #A list of zeroed out matricies corresponding to each weight matrix
        #and its dimensions
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = self.positive_gradient_Update(self.weights, nabla_w, self.zero_weights, eta, mini_batch)
        self.biases = self.positive_gradient_Update(self.biases, nabla_b, self.zero_biases, eta, mini_batch)
        #self.weights = [w+(eta/len(mini_batch))*nw
        #                for w, nw in zip(self.weights, nabla_w)]
        #self.biases = [b+ (eta/len(mini_batch))*nb
        #               for b, nb in zip(self.biases, nabla_b)]

    # Takes either the weights or biases matrix and performs the gradient descent update, ensuring that
    # all entries remain positive
    def positive_gradient_Update(self, matrices, gradients, zeros, eta, mini_batch):
        matrices = [w + (eta / len(mini_batch)) * nw
                        for w, nw in zip(matrices, gradients)]
        matrices = [np.maximum(matrix, zero) for matrix, zero in zip(matrices, zeros)]
        #for matrix in matrices :
        #    for e in np.nditer(matrix, op_flags=['readwrite']):
        #        if(e<0):
        #            e[...] = 0
        return matrices

    def backprop(self, x, y):
        """Return a tuple ``(nabla_b, nabla_w)`` representing the
        gradient for the cost function C_x.  ``nabla_b`` and
        ``nabla_w`` are layer-by-layer lists of numpy arrays, similar
        to ``self.biases`` and ``self.weights``."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(e.shape) for e in self.weights]
        # feedforward
        activation = x
        activations = [x] #list to store all the activations, layer by layer
        zs = [] #list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation) + b
            zs.append(z)
            activation = cont_or(z)
            activations.append(activation)
        #backward pass
        delta = self.likelihood_derivative(activations[-1], y)
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose()) *cont_or_prime(zs[-1])
        # Note that the variable l in the loop below is used a little
        # differently to the notation in Chapter 2 of the book.  Here,
        # l = 1 means the last layer of neurons, l = 2 is the
        # second-last layer, and so on.  It's a renumbering of the
        # scheme in the book, used here to take advantage of the fact
        # that Python can use negative indices in lists.
        for l in xrange(2, self.num_layers):
            z = zs[-l]
            cop = cont_or_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * cop
            nabla_b[-l] = delta
            e = self.weights[-l]
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def evaluate(self, test_data):
        """Return the number of test inputs for which the neural
        network outputs the correct result. Note that the neural
        network's output is assumed to be the index of whichever
        neuron in the final layer has the highest activation."""
        test_results = [(np.argmax(self.feedforward(x)), y)
                        for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)


    def likelihood_derivative(self, output_activations, y):
        """Return the vector of partial derivatives \partial C_x /
        \partial a for the output activations."""
        error = y-output_activations
        return error
        #like_derv = error/output_activations
        #return np.fmax(like_derv, error)

    def cost(self, a, y):
        return 1 / 2.0 * np.linalg.norm(y - a) ** 2


#### Miscellaneous Functions
def cont_or(z):
    return 1.0-np.exp(-z)

def cont_or_prime(z):
    return (1.0-cont_or(z))

def postive_normal(shape):
    matrix = np.random.randn(shape[0], shape[1])
    for e in np.nditer(matrix, op_flags=['readwrite']):
        e[...] = abs(e)*0.001
    return matrix