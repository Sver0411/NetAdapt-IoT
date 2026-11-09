"""Generate the current research report; v1 report remains in the archive."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name('write_refined_report.py')),run_name='__main__')
