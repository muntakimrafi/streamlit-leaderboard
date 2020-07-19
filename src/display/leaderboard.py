from typing import Dict, Optional

import streamlit as st
import pandas as pd
from streamlit.DeltaGenerator import DeltaGenerator

from src.evaluation.evaluator import Evaluator
from src.submissions.submissions_manager import SubmissionManager, SingleParticipantSubmissions


class Leaderboard:
    def __init__(self, submissions_manager: SubmissionManager,
                 evaluator: Evaluator):
        self.submissions_manager = submissions_manager
        self.evaluator = evaluator

    @st.cache(hash_funcs={SingleParticipantSubmissions: lambda x: x.submissions_hash()})
    def _get_sorted_leaderboard(self, participants_dict: Dict[str, SingleParticipantSubmissions]) -> pd.DataFrame:
        for participant in participants_dict.values():
            participant.update_results(self.evaluator)
        metric_names = [metric.name() for metric in self.evaluator.metrics()]
        leaderboard = pd.DataFrame([[pname, SingleParticipantSubmissions.get_datetime_from_path(best_result[0]),
                                     *best_result[1]] for pname, best_result in
                                    [(pname, p.get_best_result()) for pname, p in participants_dict.items()]
                                    if best_result is not None],
                                   columns=['Competitor', 'Submission Time', *metric_names])
        leaderboard = leaderboard.sort_values(by=metric_names + ['Submission Time'],
                                              ascending=[False] * len(metric_names) + [True], ignore_index=True)
        leaderboard.index += 1
        return leaderboard

    def display_leaderboard(self, leaderboard_placeholder: Optional[DeltaGenerator] = None):
        leaderboard = self._get_sorted_leaderboard(self.submissions_manager.participants)
        if leaderboard_placeholder is not None:
            leaderboard_placeholder.table(leaderboard)
        else:
            st.table(leaderboard)
