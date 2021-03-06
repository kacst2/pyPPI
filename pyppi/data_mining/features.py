"""
This module contains a method to compute features of a Protein-Protein
interaction based on two protein inputs.
"""

__all__ = ['compute_interaction_features']

from .ontology import (
    get_up_to_lca, group_terms_by_ontology_type, get_active_instance
)

DAG = None


def _split_string(value, sep=','):
    """Safe split a string removing empty/falsey strings resulting from
    the split.

    Returns
    -------
    list or None
        List of values produced by a string split, otherwise None if a falsey
        value is passed in.
    """

    if value:
        return [v.strip() for v in value.split(sep) if v.strip()]
    else:
        return None


def compute_interaction_features(source, target, dag=None):
    """Computes the textual features for an interaction between `source` and
    `target`.

    Parameters:
    ----------
    source : :class:`..database.models.Protein`
        Source protein instance.

    target : :class:`..database.models.Protein`
        Target protein instance.

    dag : dict, optional, default: None
        A dag represented by a dictionary of str accessions pointing 
        :class:`.ontology.GOTerm` instances. If None, the default global
        dag instance will be loaded, which is loaded from the `~./pyppi`
        directory.

    Returns
    -------
    dict[str, str] or None
        `None` if either protein is `None`, otherwise a `dict` mapping
        feature names to a list of computed annotations.
    """
    if dag is None:
        dag = get_active_instance()

    if source is None or target is None:
        return None

    # Turn terms for the source protein into a list
    go_mf_source = _split_string(source.go_mf)
    go_mf_source = go_mf_source if go_mf_source is not None else []
    go_mf_source = [dag[tid].id for tid in go_mf_source]

    go_bp_source = _split_string(source.go_bp)
    go_bp_source = go_bp_source if go_bp_source is not None else []
    go_bp_source = [dag[tid].id for tid in go_bp_source]

    go_cc_source = _split_string(source.go_cc)
    go_cc_source = go_cc_source if go_cc_source is not None else []
    go_cc_source = [dag[tid].id for tid in go_cc_source]

    interpro_source = _split_string(source.interpro)
    interpro_source = interpro_source if interpro_source is not None else []

    pfam_source = _split_string(source.pfam)
    pfam_source = pfam_source if pfam_source is not None else []

    keywords_source = _split_string(source.keywords)
    keywords_source = keywords_source if keywords_source is not None else []

    # Turn terms for the target protein into a list
    go_mf_target = _split_string(target.go_mf)
    go_mf_target = go_mf_target if go_mf_target is not None else []
    go_mf_target = [dag[tid].id for tid in go_mf_target]

    go_bp_target = _split_string(target.go_bp)
    go_bp_target = go_bp_target if go_bp_target is not None else []
    go_bp_target = [dag[tid].id for tid in go_bp_target]

    go_cc_target = _split_string(target.go_cc)
    go_cc_target = go_cc_target if go_cc_target is not None else []
    go_cc_target = [dag[tid].id for tid in go_cc_target]

    interpro_target = _split_string(target.interpro)
    interpro_target = interpro_target if interpro_target is not None else []

    pfam_target = _split_string(target.pfam)
    pfam_target = pfam_target if pfam_target is not None else []

    keywords_target = _split_string(target.keywords)
    keywords_target = keywords_target if keywords_target is not None else []

    # Prepare the ulca terms and combined lists
    terms = get_up_to_lca(go_mf_source, go_mf_target) + \
        get_up_to_lca(go_bp_source, go_bp_target) + \
        get_up_to_lca(go_cc_source, go_cc_target)

    # The ulca inducer will mix up the ontology types since the part_of
    # relationship can cross-link between ontologies. This may result
    # in some terms being induced more than twice so re-group them
    # and apply a filter.
    grouped = group_terms_by_ontology_type(terms, max_count=2)
    ulca_go_mf = [dag[tid].id for tid in grouped['mf']]
    ulca_go_bp = [dag[tid].id for tid in grouped['bp']]
    ulca_go_cc = [dag[tid].id for tid in grouped['cc']]

    go_mf = list(go_mf_source) + list(go_mf_target)
    go_bp = list(go_bp_source) + list(go_bp_target)
    go_cc = list(go_cc_source) + list(go_cc_target)
    interpro = list(interpro_source) + list(interpro_target)
    pfam = list(pfam_source) + list(pfam_target)
    keywords = list(keywords_source) + list(keywords_target)

    features = dict(
        go_mf=go_mf, go_bp=go_bp, go_cc=go_cc,
        ulca_go_mf=ulca_go_mf, ulca_go_bp=ulca_go_bp, ulca_go_cc=ulca_go_cc,
        interpro=interpro, pfam=pfam, keywords=keywords
    )
    return features
