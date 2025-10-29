import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
root = Path(__file__).resolve().parents[3]
core_init = root / 'core' / '__init__.py'
spec = spec_from_file_location('core', core_init, submodule_search_locations=[str(root / 'core')])
module = module_from_spec(spec)
sys.modules['core'] = module
spec.loader.exec_module(module)
globals().update(module.__dict__)
