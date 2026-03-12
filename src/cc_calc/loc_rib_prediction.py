"""Prediction of Loc-RIB models."""

from collections import deque

from cc_calc.as_path import ASPath
from cc_calc.as_rel_graph import ASRelGraph
from cc_calc.autonomous_system import AS
from cc_calc.loc_rib_model import LocRIBModel
from cc_calc.prefix_sure_as_path_list import PrefixSureASPathList


def _add_sure_path_recursively(path: ASPath, model: LocRIBModel) -> None:
    for i in range(len(path)):
        last_as = path[i]

        if last_as is not None:
            model.add_path(last_as, path[i + 1 :], sureness=True)


def _insert_sure_paths(sure_paths: PrefixSureASPathList, model: LocRIBModel) -> None:
    for path in sure_paths:
        _add_sure_path_recursively(path, model)


def _collect_base_as_set(sure_paths: PrefixSureASPathList) -> set[AS]:
    return {_as for path in sure_paths for _as in path}


def predict_loc_rib_model(
    as_rel_graph: ASRelGraph,
    sure_paths: PrefixSureASPathList,
) -> LocRIBModel:
    """Fits a Loc-RIB model to the provided data.

    Args:
        as_rel_graph: An AS relationship graph.
        sure_paths: A list of sure AS paths to a prefix.

    Returns: A fitted Loc-RIB model.
    """
    model = LocRIBModel(sure_paths.prefix)

    update_queue: deque[AS] = deque()

    _insert_sure_paths(sure_paths, model)

    for _as in _collect_base_as_set(sure_paths):
        update_queue.append(_as)

    while len(update_queue) != 0:
        updated_as = update_queue.popleft()
        as_path = model.best_path(updated_as)

        appended_path = as_path.append(updated_as)

        prev_as = as_path[0]

        peers = as_rel_graph.bgp_receivers_from_as(updated_as, prev_as)

        for peer in peers:
            updated = model.add_path(peer, appended_path)

            if updated:
                update_queue.append(peer)

    return model
