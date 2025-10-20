"""
Processor to export per-product Phase 1 and Phase 3 start/end dates and success flags.
Assumptions due to API data limitations:
- Phase-specific dates are not explicitly provided by ClinicalTrials.gov v2 API for most studies.
- We approximate phase start as overall start_date when the phase is listed for the study.
- We approximate phase end as primary_completion_date (fallback to completion_date) when the study progressed to or beyond the phase or is completed.
- A phase is marked failed (0) if the study status is TERMINATED, WITHDRAWN, or SUSPENDED and did not clearly progress beyond that phase.
These heuristics can be refined if more granular per-phase dates become available.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv

from models import ClinicalTrial
from config import OUTPUT_DIRECTORY


FAILED_STATUSES = {"TERMINATED", "WITHDRAWN", "SUSPENDED"}
ONGOING_OR_COMPLETED_STATUSES = {
    "RECRUITING",
    "ACTIVE_NOT_RECRUITING",
    "COMPLETED",
    "ENROLLING_BY_INVITATION",
    "NOT_YET_RECRUITING",
    "UNKNOWN"
}


@dataclass
class PhaseDatesRow:
    company: Optional[str]
    product: str
    disorder_or_condition: Optional[str]
    nct_id: str
    phase1_start: Optional[str]
    phase1_end: Optional[str]
    phase1_success: int
    phase3_start: Optional[str]
    phase3_end: Optional[str]
    phase3_success: int

    def to_csv_row(self) -> List[Any]:
        return [
            self.company or "",
            self.product,
            self.disorder_or_condition or "",
            self.nct_id,
            self.phase1_start or "",
            self.phase1_end or "",
            self.phase1_success,
            self.phase3_start or "",
            self.phase3_end or "",
            self.phase3_success,
        ]


class PhaseDatesProcessor:
    """Exports per-product Phase 1/3 start/end dates and success flags."""

    def __init__(self, output_dir: str = OUTPUT_DIRECTORY):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.phase_dir = self.output_dir / "phase_dates"
        self.phase_dir.mkdir(exist_ok=True)

    def export_phase_dates(self, trials: List[ClinicalTrial], filename_prefix: str = "phase_dates") -> str:
        rows: List[PhaseDatesRow] = []
        for trial in trials:
            rows.extend(self._trial_to_rows(trial))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = self.phase_dir / f"{filename_prefix}_{timestamp}.csv"

        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Company",
                "Product",
                "Disorder/Condition",
                "NCT ID",
                "Phase1 Start",
                "Phase1 End",
                "Phase1 Success",
                "Phase3 Start",
                "Phase3 End",
                "Phase3 Success",
            ])
            for r in rows:
                writer.writerow(r.to_csv_row())

        return str(out_path)

    def _trial_to_rows(self, trial: ClinicalTrial) -> List[PhaseDatesRow]:
        company = trial.sponsors[0].name if trial.sponsors else None
        conditions = ", ".join([c.name for c in trial.conditions]) if trial.conditions else None
        phase_names = (trial.current_phase or "").upper()
        has_p1 = "PHASE1" in phase_names or "EARLY_PHASE1" in phase_names
        has_p3 = "PHASE3" in phase_names

        # We use overall dates as proxies
        start_date_iso = trial.start_date.isoformat() if trial.start_date else None
        end_date_iso = (trial.primary_completion_date or trial.completion_date).isoformat() if (trial.primary_completion_date or trial.completion_date) else None

        # Determine success flags by simple heuristic
        def phase_success(target_phase: str) -> int:
            if trial.status in FAILED_STATUSES:
                # If failed and didn't clearly progress beyond phase, mark 0
                progressed_beyond = False
                if target_phase == "PHASE1" and ("PHASE2" in phase_names or "PHASE3" in phase_names or "PHASE4" in phase_names):
                    progressed_beyond = True
                if target_phase == "PHASE3" and ("PHASE4" in phase_names):
                    progressed_beyond = True
                return 1 if progressed_beyond else 0
            # Otherwise assume not failed in that phase
            return 1

        rows: List[PhaseDatesRow] = []
        # Emit one row per intervention (product)
        if trial.interventions:
            for intervention in trial.interventions:
                p1_start = start_date_iso if has_p1 else None
                p1_end = end_date_iso if has_p1 else None
                p3_start = start_date_iso if has_p3 else None
                p3_end = end_date_iso if has_p3 else None

                rows.append(PhaseDatesRow(
                    company=company,
                    product=intervention.name,
                    disorder_or_condition=conditions,
                    nct_id=trial.nct_id,
                    phase1_start=p1_start,
                    phase1_end=p1_end,
                    phase1_success=phase_success("PHASE1") if has_p1 else 0,
                    phase3_start=p3_start,
                    phase3_end=p3_end,
                    phase3_success=phase_success("PHASE3") if has_p3 else 0,
                ))
        else:
            # If no interventions, still emit a row for the study (product unknown)
            rows.append(PhaseDatesRow(
                company=company,
                product="",
                disorder_or_condition=conditions,
                nct_id=trial.nct_id,
                phase1_start=start_date_iso if has_p1 else None,
                phase1_end=end_date_iso if has_p1 else None,
                phase1_success=phase_success("PHASE1") if has_p1 else 0,
                phase3_start=start_date_iso if has_p3 else None,
                phase3_end=end_date_iso if has_p3 else None,
                phase3_success=phase_success("PHASE3") if has_p3 else 0,
            ))

        return rows
