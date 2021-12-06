from django import template

register = template.Library()


@register.simple_tag
def unique_id_for_filter(pk, forloopcounter):
    return str(pk) + "-" + str(forloopcounter)


@register.filter
def index(indexable, index):
    return indexable[index]

@register.filter
def filter(log):
    return log.filter

@register.filter
def create_ref_url(url, ref):
    return "&".join(url.strip().split("&")[0:-1]) + "&ref=" + str(ref)


@register.filter
def get_graph(log, reference):
    return log.graph(reference)


@register.filter
def get_metrics(log, reference):
    return log.metrics(reference)

@register.filter
def similarity(log, reference):
    return log.get_similarity_index(reference)