import srcNN.data.mnist_loader
import srcNN.network.network_factory as nf
import srcNN.network.network_runner as nr


def build_hyps(eta1, eta2, ws, num_layers):
    if num_layers == 3:
        return [eta1, (eta2, ws), eta1]
    if num_layers == 4:
        return [eta1, eta1, (eta2, ws), eta1]
    raise NotImplementedError("No case for the arguments passed")


def grid_search(sizes, act_strings, eta1_grid_1, eta2_grid_2, ws_grid):
    # Load the data
    training_data, validation_data, test_data = srcNN.data.mnist_loader.load_data_wrapper()
    runner = nr.NetworkRunner()

    #File to store results
    f = load_file(act_strings, sizes)
    num_layers = len(sizes) - 1

    for eta1 in eta1_grid_1:
        for eta2 in eta2_grid_2:
            for ws in ws_grid:
                hypers = build_hyps(eta1, eta2, ws, num_layers)
                network = nf.mix_network(sizes, act_strings, hypers)
                val_er = runner.sgd(network, training_data, 10, 50, validation_data)
                to_file(f, hypers, val_er)

def grid_search_2_logics(sizes, act_strings, eta_grid, ws_grid_1, ws_grid_2):
    # Load the data
    training_data, validation_data, test_data = srcNN.data.mnist_loader.load_data_wrapper()
    runner = nr.NetworkRunner()

    # File to store results
    f = load_file(act_strings, sizes)

    for eta in eta_grid:
        for ws1 in ws_grid_1:
            for ws2 in ws_grid_2:
                hypers = [eta, (eta, ws1), (eta, ws2), eta]
                network = nf.mix_network(sizes, act_strings, hypers)
                val_er = runner.sgd(network, training_data, 10, 50, validation_data)
                to_file(f, hypers, val_er)



def grid_search_vanilla(sizes, act_strings, eta_grid):
    # Load the data
    training_data, validation_data, test_data = srcNN.data.mnist_loader.load_data_wrapper()
    runner = nr.NetworkRunner()

    #File to store results
    f = load_file(act_strings, sizes)
    num_layers = len(sizes) - 1

    for eta in eta_grid:
        hypers = [eta] * num_layers
        network = nf.mix_network(sizes, act_strings, hypers)
        val_er = runner.sgd(network, training_data, 10, 50, validation_data)
        to_file(f, hypers, val_er)

def grid_search_or_and(sizes, act_strings, eta_grid1, eta_grid2):
    # Load the data
    training_data, validation_data, test_data = srcNN.data.mnist_loader.load_data_wrapper()
    runner = nr.NetworkRunner()

    # File to store results
    f = load_file(act_strings, sizes)

    for eta1 in eta_grid1:
        for eta2 in eta_grid2:
            hypers = [(eta1, 0.01), (eta2, 0.001)]
            network = nf.mix_network(sizes, act_strings, hypers)
            val_er = runner.sgd(network, training_data, 10, 50, validation_data)
            to_file(f, hypers, val_er)



def load_file(act_strings, sizes):
    #Prep the name
    name = ''
    for a in act_strings:
        name += a+'-'
    for s in sizes[:-1]:
        name += str(s)+'-'
    name+= str(sizes[-1])

    #Create the file
    return open(name, 'w')

def to_file(f, hypers, val_error):
    f.write(str(hypers)+'\n')
    for err in val_error:
        f.write(str(err)+'\n')
    f.write('\n')
    return f

#grid_search_2_logics([784, 30, 30, 30, 10], ['sig', 'or', 'and', 'sm'], [0.3], [0.1], [0.1])