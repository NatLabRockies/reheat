import pandas as pd
import numpy as np
import json


class Params():

    def __init__(self, REHEAT_PATH):
        
        self.heating_demand_MWh = pd.read_csv(REHEAT_PATH / 'inputs/heating_loads/heatingload_MWhBoulderCO.csv', header=None, index_col=False)[0].to_numpy()
    
        self.FPC_generation_MWh = pd.read_csv(REHEAT_PATH / 'inputs/fpc_generation/fpc_MWm2_BoulderCO.csv', header=None, index_col=False)[0].to_numpy()

        self.price_energy = np.load(REHEAT_PATH / 'inputs/electricity_prices/price_elec.npy')[:, 0]
        self.price_demand = 20
        self.price_NG = 9.78/0.29  # $/kft3 * (kft3/MWh)
            
        self.COP_IHP = 3
        
        self.SOC_TES_i = 0
        
        self.capex_var_IHP = 800*1000  # $/MW
        self.capex_var_NGB = 120*1000  # $/MW
        self.capex_var_FPC = 1000*1000  # $/MW
        
        self.capex_var_TES = 10*1000  # $/MWh
        self.capex_var_TES_diff = 0*1e3  #= 300*1000  # $/MW

        self.carbon_offset_price = 10  # $/ton_co2
        self.emission_factor = 0.55  # ton_co2/MWh_natural_gas


    # def initialize_params_json(input_path=REHEAT_PATH/'inputs/input.json'):

    #     # load input.json file
    #     with open(input_path, "r") as file:
    #         input = json.load(file)

    #     p = Params()

    #     ################
    #     # Heat Generation
    #     ################

    #     p.solar_generation_MWh = {}
    #     p.solar_capex_var = {}
    #     for tech in input['heat_generation']['solar']:
    #         name = tech['name']
    #         p.solar_generation_MWh[name] = pd.read_csv(tech['file_path'], header=None, index_col=False)[0].to_numpy()
    #         p.solar_capex_var[name] = tech['capex_dollar_per_kw']*1000  # $/MW

    #     p.heating_demand_MWh = pd.read_csv(input['heat_demand']['file_path'], header=None, index_col=False)[0].to_numpy()
        
    #     p.price_energy = np.load(input['utility_prices']['electricity']['energy_dollar_per_kwh_file_path'])[:, 0]
    #     p.price_demand = input['utility_prices']['electricity']['demand_dollar_per_kw']
    #     p.price_NG = input['utility_prices']['fuel']['dollar_per_kwh']  # $/kft3 * (kft3/MWh)
            
    #     p.COP_IHP = 3
        
    #     p.SOC_TES_i = 0
        
    #     p.capex_var_IHP = 800*1000  # $/MW
    #     p.capex_var_NGB = 102*1000  # $/MW
    #     p.capex_var_FPC = 4000*1000  # $/MW
        
    #     p.capex_var_TES = 10*1000  # $/MWh
    #     p.capex_var_TES_diff = 0*1e3  #= 300*1000  # $/MW

    #     p.carbon_offset_price = 10  # $/ton_co2
    #     p.emission_factor = 0.55  # ton_co2/MWh_natural_gas
        
    #     return p
