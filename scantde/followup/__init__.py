"""
Automation and follow-up tools for Scantde.
"""
from scantde.followup.cuts import apply_base_spec_cuts
from scantde.followup.infant import infant_assignment
from scantde.followup.sedm import apply_sedm_cuts, sedm_assignment
from scantde.followup.soar import soar_assignment
from scantde.followup.slack import send_table_to_slack
from scantde.followup.candidates import get_candidate_summary