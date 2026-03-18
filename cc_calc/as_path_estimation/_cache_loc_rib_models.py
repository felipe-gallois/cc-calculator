from cc_calc.as_path_estimation._as_rel_graph import ASRelGraphRepository
from cc_calc.as_path_estimation._loc_rib_model import LocRIBModelRepository
from cc_calc.as_path_estimation._loc_rib_prediction import predict_loc_rib_model
from cc_calc.as_path_estimation._prefix_sure_as_path_list import (
    PrefixSureASPathListRepository,
)
from cc_calc.logging import Logger


class CacheLocRIBModelsError(Exception):
    pass


class CacheLocRIBModels:
    def __init__(
        self,
        rel_graph_repo: ASRelGraphRepository,
        sure_path_list_repo: PrefixSureASPathListRepository,
        loc_rib_model_repo: LocRIBModelRepository,
        logger: Logger,
    ) -> None:
        self._rel_graph_repo = rel_graph_repo
        self._sure_path_list_repo = sure_path_list_repo
        self._loc_rib_model_repo = loc_rib_model_repo

    def cache_models(self) -> None:
        try:
            rel_graph = self._rel_graph_repo.load_rel_graph()
            sure_path_lists = self._sure_path_list_repo.load_all_sure_path_lists()

            for sure_path_list in sure_path_lists:
                prefix = sure_path_list.prefix

                model = predict_loc_rib_model(rel_graph, sure_path_list)

                self._loc_rib_model_repo.save_model(model)
        except Exception as e:
            raise CacheLocRIBModelsError("Cannot find AS relationship graph") from e
