import numpy as np
import scipy
from network import Network
from network_matrix import MatrixNetwork
from activations import *
from optimizers import *
from dropout import *

def mix_network(sizes, acts, hyp_params, drop=(None, None), reg=False, no_biases=False):
    """Creates and returns a nerual network.

    This creation includes:
    - initializing the weights at each layer
    - creating the activations at each layer
    - creating the optimizer at each layer, e.g. sgd with reguralisation
    - initializing the Dropout scheme, if there is any

    Keyword arguments:
       sizes -- The integer sizes of each layer of the network

       acts -- A list of strings that correspond to the activation to be
       produced at each layer. E.g. ['relu', 'sm']. This must always be
       one element shorter than sizes, because there is no activation on
       the input layer

       hyp_params -- A list of hyper_parameter scalars/tuples the same
       length as acts. Usually, each element will be the learning rate
       for that layer, however some activation require additional hyper-
       params, in which case a tuple should be used.

       drop -- A binary tuple specifying the drop out scheme. The first
       element specifies the type of DropOut scheme e.g. 'dropout'. The
       second element n, specifies the keep probability 1/n

       reg -- If true, sgd with regularisation will be used, if false
       vanilla sgd will be used.

       no_biases - If true, the biases will be set to zero and sgd will
       not update them.

    """
    #Construct the weights and biases
    weights, biases = [], []
    prev_act = None
    for act, hp, s0, s1 in zip(acts, hyp_params, sizes[:-1], sizes[1:]):
        #Check for nors, which produce 2 outputs
        if(prev_act == 'nor'):
            s0 *= 2
        w, b = __construct_w_b(act, s0, s1, hp, no_biases)
        weights.append(w)
        biases.append(b)
        prev_act = act

    #Construct each activation
    activations = []
    for act, hp, width in zip(acts, hyp_params, sizes[1:]):
        activations.append(__construct_act(act, hp, width, reg, no_biases))

    #Create the name
    name = __create_name(acts)

    #Determine the dropout scheme
    d_name, n = drop
    if d_name == 'drop_out':
        drop_scheme = DropOut(sizes, n)
    elif d_name == 'drop_sys':
        drop_scheme = DropSys(sizes, n)
    elif d_name == 'drop_connect':
        drop_scheme = DropConnect(sizes, n)
    else:
        drop_scheme = DropNull()

    #return Network(weights, biases, activations, name=name, drop_scheme=drop_scheme)
    return MatrixNetwork(weights, biases, activations, name=name, drop_scheme=drop_scheme)


def relu_with_linear_final(sizes, eta, weights=None, biases=None):
    """Construct a relu with a linear output layer, useful for regression problems"""
    if (biases == None):
        biases = [np.ones((y, 1)) for y in sizes[1:]]

    if (weights == None):
        weights = [1.0 / float(x) ** 0.5 *(np.random.randn(y, x))
                        for x, y in zip(sizes[:-1], sizes[1:])]

    activations = __construct_activations(sizes[1:-1], eta)
    return Network(weights, biases, activations)


def saxe_init(sizes, acts, hyp_params, sigma31, use_saxe_weights):
    """Create a network initialized for Saxe training, i.e.
    orthogonal weights and no biases"""
    #Saxe initialization of the weights
    weights, U, S, Vt = __svd_weights(sizes, sigma31, use_saxe_weights)
    biases = [np.zeros((s, 1)) for s in sizes[1:]]
    #Create activations
    activations = [__construct_act(act, hp, w, no_biases=True)
            for act, hp, w in zip(acts, hyp_params, sizes[1:])]
    return Network(weights, biases, activations), U, S, Vt



def __svd_weights(sizes, sigma31, use_saxe_weights):
    """Initialize the weights according to the SVD of the output-input
    covariance matrix, as specified on page 5 of the Saxe paper"""
    #SVD of the covariance matrix
    U, s, Vt = scipy.linalg.svd(sigma31)
    #Random orthogonal matrix
    R = __rvs(dim=sizes[1])
    #Diagonal smalll starting conditions
    Da = __small_random_rect_diag(sizes[2], sizes[1])
    Db = __small_random_rect_diag(sizes[1], sizes[0])
    #Create the weight matracies
    if use_saxe_weights:
        W32 = U.dot(Da).dot(R.transpose())
        W21 = R.dot(Db).dot(Vt)
    else:
        W32 = 0.025 * np.random.randn(sizes[2], sizes[1])
        W21 = 0.025 *np.random.randn(sizes[1], sizes[0])
    #Matrix for the singualr values
    S = __small_random_rect_diag(sizes[2], sizes[0])
    for i in xrange(sizes[2]):
        S[i, i] = s[i]

    return [W21, W32], U, S, Vt

def __small_random_rect_diag(m, n):
    """Return a rectangular diagonal matrix with small uniform random
    diagonals"""
    if m <= n:
        return __diag_helper(m, n)
    return __diag_helper(n, m).transpose()

def __diag_helper(sm, big):
    I = np.identity(sm)
    zeros = np.zeros((sm, big - sm))
    #Small random initial constant values
    I *= np.random.uniform(0, 0.05, (sm, sm))
    return np.concatenate((I, zeros), axis=1)


def __construct_activations(relu_widths, eta):
    sgd = Sgd(eta)
    activations = []
    for width in relu_widths:
        activations.append(Relu(width, sgd))
    activations.append(Linear(sgd))
    return activations

# def pure_or(sizes):
#     weights = [__postive_normal(y, x)
#                for x, y in zip(sizes[:-1], sizes[1:])]
#     biases = [__postive_normal(y, 1)
#               for y in sizes[1:]]
#     num_layers = len(sizes)
#     activations = [NoisyOr() for i in xrange(num_layers)]
#     return Network(weights, biases, activations, keep_positive_sgd)

def __positive_normal(c, s1, s0):
    return c*abs(np.random.randn(s1, s0))


def __construct_w_b(act_string, s0, s1, hyp_params, no_biases):
    xc = 1.0 / float(s0) ** 0.5
    if act_string == 'sig':
        weights = 16 * xc * np.random.randn(s1, s0)
        biases = 16* xc* np.random.randn(s1, 1)
    elif act_string == 'tanh' or act_string == 'lin':
        weights = xc * np.random.randn(s1, s0)
        biases = xc * np.random.randn(s1, 1)
    elif act_string == 'or' or act_string == 'and' or act_string == 'nor':
        w_scale = xc * hyp_params[1]
        weights = __positive_normal(w_scale, s1, s0)
        biases = __positive_normal(w_scale, s1, 1)
    elif act_string == 'sm':
        weights = xc * np.random.randn(s1, s0)
        biases =  xc * np.random.randn(s1, 1)
    elif act_string == 'relu':
        weights = xc* np.random.randn(s1, s0)
        biases = 0.1 * np.random.randn(s1, 1)
    else:
        raise NotImplementedError('Factory does not handle the constuction of the activation: ' + act_string)
    if no_biases:
        biases = np.zeros((s1, 1))
    return weights, biases


def __construct_act(act_string, hp, width, reg=False, no_biases=False):

    if act_string == 'sig':
        sgd = create_sgd(hp, reg, no_biases)
        return Sigmoid(sgd)
    if act_string == 'tanh':
        sgd = create_sgd(hp, reg, no_biases)
        return Tanh(sgd)
    if act_string == 'or' or act_string == 'nor':
        eta = hp[0]
        pos_sgd = create_pos_sgd(eta, reg)
        if act_string == 'nor':
            return NoisyOrNegable(pos_sgd)
        return NoisyOr(pos_sgd)
    if act_string == 'and':
        eta = hp[0]
        pos_sgd = create_pos_sgd(eta, reg)
        return NoisyAnd(pos_sgd)
    if act_string == 'sm':
        sgd = create_sgd(hp, reg, no_biases)
        return Softmax(sgd)
    if act_string == 'relu':
        sgd = create_sgd(hp, reg, no_biases)
        return Relu(width, sgd)
    if act_string == 'lin':
        sgd = create_sgd(hp, reg, no_biases)
        return Linear(sgd)

    raise NotImplementedError('Factory does not handle the constuction of the activation: '+act_string)

def __create_name(act_strings):
    name = ''
    for act in act_strings[:-1]:
        name+=act+'-'
    return name+act_strings[-1]

def __rvs(dim=3):
    random_state = np.random
    H = np.eye(dim)
    D = np.ones((dim,))
    for n in range(1, dim):
        x = random_state.normal(size=(dim - n + 1,))
        D[n - 1] = np.sign(x[0])
        x[0] -= D[n - 1] * np.sqrt((x * x).sum())
        # Householder transformation
        Hx = (np.eye(dim - n + 1) - 2. * np.outer(x, x) / (x * x).sum())
        mat = np.eye(dim)
        mat[n - 1:, n - 1:] = Hx
        H = np.dot(H, mat)
        # Fix the last sign such that the determinant is 1
    D[-1] = (-1) ** (1 - (dim % 2)) * D.prod()
    # Equivalent to np.dot(np.diag(D), H) but faster, apparently
    H = (D * H.T).T
    return H

