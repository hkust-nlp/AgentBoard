def cartesian_product(sequences):
    # TODO: Rename this. It's not good that we have two functions
    # called "product" and "cartesian_product", of which "product"
    # computes cartesian products, while "cartesian_product" does not.

    # This isn't actually a proper cartesian product because we
    # concatenate lists, rather than forming sequences of atomic elements.
    # We could probably also use something like
    # map(itertools.chain, product(*sequences))
    # but that does not produce the same results
    if not sequences:
        yield []
    else:
        temp = list(cartesian_product(sequences[1:]))
        for item in sequences[0]:
            for sequence in temp:
                yield item + sequence


def get_peak_memory_in_kb():
    try:
        # This will only work on Linux systems.
        with open("/proc/self/status") as status_file:
            for line in status_file:
                parts = line.split()
                if parts[0] == "VmPeak:":
                    return int(parts[1])
    except OSError:
        pass
    raise Warning("warning: could not determine peak memory")
