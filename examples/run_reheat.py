from pathlib import Path
from reheat import initialize_params, run_optimization

if __name__ == "__main__":
   
   data_root = Path(__file__).parent.parent / "data"
   
   params = initialize_params()
   results = run_optimization(params, print_flag=True, solver="amplxpress")
   
   results.print_results()