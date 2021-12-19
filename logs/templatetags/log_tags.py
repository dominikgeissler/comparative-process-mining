from django import template

register = template.Library()


@register.simple_tag
def unique_id_for_filter(pk, forloopcounter):
    """creates a unique id for the filter.html by combining the handlers pk and its position in the table"""
    return str(pk) + "-" + str(forloopcounter)


@register.filter
def index(indexable, index):
    """returns the 'index'-th element of a list"""
    return indexable[index]

@register.filter
def filter(log):
    """returns the filter of the log"""
    return log.filter

@register.filter
def create_ref_url(url, ref):
    """creates the 'change reference' link"""
    return "&".join(url.strip().split("&")[0:-1]) + "&ref=" + str(ref)


@register.filter
def get_graph(log, reference):
    """return the g6 graph of a log relative to its reference"""
    return log.graph(reference)


@register.filter
def get_metrics(log, reference):
    """return the metrics of a log relative to its reference"""
    return log.metrics(reference)

@register.filter
def similarity(log, reference):
    """return the similarity index of a log relative to its reference"""
    return log.get_similarity_index(reference)