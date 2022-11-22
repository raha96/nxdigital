
def synthesize_lock(one_probability:float, number_of_bits:int, verbose:bool=False):
    """Synthesize a lock g function based on CAS lock architecture"""
    out = ""
    p = one_probability
    k = number_of_bits

    from math import floor
    numones = floor(float(2**k) * p)
    if numones % 2 == 0:
        numones += 1

    if verbose:
        targetprob = float(numones) / float(2**k)
        print (f"The target probability is {targetprob}.")

    for i in range(k):
        p *= 2.0
        if p >= 1.0:
            out = "|" + out
            p -= 1.0
        else:
            out = "&" + out
        #if numones & 1:
        #    out += "|"
        #else:
        #    out += "&"
        #numones >>= 1

    if verbose:    
        print (f"The residual probability (for the first input) is {p}.")

        realprob = 0.5
        for c in out:
            realprob *= 0.5
            if c == '|':
                realprob += 0.5
        print (f"The one-probability of the synthesized function is {realprob}.")

    return out
