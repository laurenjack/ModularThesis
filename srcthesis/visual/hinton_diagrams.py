import srcthesis.network.network_factory as nf
import srcthesis.network.network_runner as nr
import srcthesis.run.mnist_loader as ml
import srcthesis.data.optimal_nets as on
import matplotlib.pyplot as plt
import numpy as np

def pick(training_data, digit):
    """For example, if digit=2, pick the first 2 in the training data"""
    for x, y in training_data:
        if y[digit][0] == 1.0:
            return x
    return None

def get_weights_of_maximal(network, x, l):
    a = network.feedforward_to(x, l)
    to_histogram(a)
    max_index = np.argmax(a)
    return network.weights[l-1][max_index]

def get_weights_and_inds_over(t, ws_of_maximal):
    weights = []
    inds = []
    for i in xrange(ws_of_maximal.shape[0]):
        w = ws_of_maximal[i]
        if w > t:
            weights.append(w)
            inds.append(i)
    return weights, inds

def to_histogram(w):
    plt.figure(1)
    plt.hist(w.flatten(), bins=50, normed=True, stacked=True)

def w_to_hinton(w, fig_num):
    plt.figure(fig_num, facecolor="white")
    ax = plt.gca()
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    plt.imshow(w, interpolation="nearest" ,cmap='Greys')

def plot_feature_map_for(big_weights, neuron_indexes, network):
    fig_num = 2
    image_sum = np.zeros((28, 28))
    for bw, ind in zip(big_weights, neuron_indexes):
        w = network.weights[0][ind]
        as_image = w.reshape(28, 28)
        image_sum += bw*(1.0- as_image)
        w_to_hinton(as_image, fig_num)
        fig_num += 1
    image_sum = np.exp(-image_sum)
    w_to_hinton(image_sum, fig_num)





# Load network hyper-parameters
sizes, act_strings, hypers = on.get_optimal('sig-sm')
#hypers = [hypers[1], hypers[1]]
#network = nf.mix_network([784, 30, 10], ['or', 'or'], hypers)
network = nf.mix_network(sizes, act_strings, hypers)

# Load the data
training_data, validation_data, test_data = ml.load_data_wrapper()
# Make validation data trainable
val_inputs = [x for x, y in validation_data]
validation_results_vec = [ml.vectorized_result(y) for x, y in validation_data]
validation_data = zip(val_inputs, validation_results_vec)
training_data.extend(validation_data)
runner = nr.NetworkRunner()

#Train the network
test_errors = runner.sgd_tracking_error(network, training_data, 10, 60, test_data)

#Pick the first two from the training data
x = pick(training_data, 5)

#Get the maximally executing AND neuron's weights
ws_of_maximal = get_weights_of_maximal(network, x, 2)

#Get all the big, non-negilgible weights from this maximal neuron
big_ws, big_inds = get_weights_and_inds_over(0.1, ws_of_maximal)

#Finally, draw the feature maps that correspond to these
plot_feature_map_for(big_ws, big_inds, network)
print big_ws
plt.show()








# for i in xrange(1):
#     print network.weights[2][:, i]
#     w_to_hinton(network.weights[0][i].reshape(28,28), i+1)
#     w_to_hinton(network.weights[1], i + 1)
#     to_histogram(network.weights[1])
# plt.show()
