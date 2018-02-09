import ipaddress
import pandas as pd


def process_traceroutes(db):

    result_list = list(db.results.find())
    df_traceroutes = pd.DataFrame(result_list)
    df_traceroutes['hops'] = df_traceroutes['result'].map(lambda x: len(x))
    df_traceroutes.drop(
        [u'size',
         u'timestamp',
         u'type',
         u'group_id',
         u'msm_id',
         u'msm_name',
         u'paris_id',
         u'fw',
         u'af',
         u'endtime',
         u'dst_name',
         u'proto',
         u'lts',
         u'result'
         ], 1, inplace=True
    )
    df_traceroutes.columns = ['_id',
                              'target',
                              'origin', 'probe', 'src_addr', 'hops']
    return df_traceroutes


class NoneResponsive(object):
    """
    Basic class to deal with non-responsive hops
    """
    def __init__(self, int_id):
        self.id = int_id

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """
        Override the default hash behavior
        (that returns the id or the object)
        """
        return hash(tuple(sorted(self.__dict__.items())))

    def __str__(self):
        return u'Non_responsive_{}'.format(int(self.id))

    def __repr__(self):
        return u'Non_responsive_{}'.format(int(self.id))


def non_responsive_generator():
    """
    Returns a new non-responisve object with a new id
    """
    count_id = 0
    while 1:
        yield NoneResponsive(count_id)
        count_id = count_id + 1


def replace_with_nones(A, gen):
    """
    Given a list and a non-responisve generator, replaces consecutive
    None elements with a single non responsive hops
    """
    to_remove = []
    going = False
    for i, x in enumerate(A):
        if not x and not going:
            going = True
            start = i
        if x and going:
            to_remove.append((start, i, [(gen.next(), i-start)]))
            going = False
    if going:
        to_remove.append((start, len(A)+1, [(gen.next(), len(A)-start)]))

    for (start, end, val) in to_remove[::-1]:
        A[start:end] = val


def ultimo_caida(L):
    """
        Starting from the end, get the first not none
    """
    return next((x.origin for x in L[::-1] if x.origin), None)


def first_duplicate(A):
    """
    Return the first element that appears duplicated in the list
    """
    return next((x for i, x in enumerate(A) if A[:i].count(x) > 0), None)


def links_from_traceroute(tr,
                          non_gen,
                          add_first=True,
                          keep_last=True,
                          keep_none=True
                          ):
    """
    It takes as an argument a ripe.atlas.sagan.traceroute.TracerouteResponse
    and returns a set of tuples (ipaddress,ipaddress) of the infered links
    Non responsive consecutive hops are trated as one.
    Destination in preserved
    Source is added to the beginning
    """
    # For each hop get one element
    trace_partial = [ultimo_caida(h.packets) for h in tr.hops]
    # Add the source IP to the trace
    if add_first:
        trace_partial = [tr.origin] + trace_partial
    # Remove the last one if don't keep it
    if not keep_last:
        trace_partial = trace_partial[:-1]
    # Instanciate ipaddress using ipaddress module
    trace_partial = [ipaddress.ip_address(x.decode('unicode-escape'))
                     if x else None for x in trace_partial]
    # Truncates the list in the fist duplicate assuming a loop
    if first_duplicate(trace_partial):
        trauncate_index = [i for i, x in enumerate(trace_partial)
                           if x == first_duplicate(trace_partial)][1]
        trace_partial = trace_partial[:trauncate_index]

    # Treat private as non-responsive
    for i, x in enumerate(trace_partial):
        if x and x.is_private:
            trace_partial[i] = None
    # Replace Nones with 1 non-responsive
    if keep_none:
        replace_with_nones(trace_partial, non_gen)

    # Return all links between pair of hops
    return set([(h1, h2) for h1, h2 in zip(trace_partial, trace_partial[1:])
                if h1 and h2]), trace_partial
