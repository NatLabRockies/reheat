import numpy as np
import matplotlib.pyplot as plt
from pyomo.environ import *
import pickle
import cloudpickle
from datetime import datetime
import os
from pathlib import Path

from .params import Params
from .results import Results

FILE_PATH = Path(__file__).parent.resolve()
REHEAT_PATH = Path(__file__).parent.parent.resolve()

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12
plt.rcParams["figure.figsize"] = (15, 10)

# time horizon
n_days = 365
n_hours = 24
n_t = n_days*n_hours
n_m = int(np.ceil(n_days/31))
n_days_in_each_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def create_model():

    m = ConcreteModel()
    # m.dual = Suffix(direction=Suffix.IMPORT)

    # index sets (RangeSet is used for non-numerical or non-ordered indices, prevents initializing parameters)
    m.T = range(8760)  # all time steps
    m.M = range(12)  # months in the year
    m.D = range(1)  # demand periods

    return m


def initialize_params():
    
    return Params(REHEAT_PATH)


def add_params(m, params):
               
    m.capex_var_IHP = Param(initialize=params.capex_var_IHP)  # $/MW
    m.capex_var_NGB = Param(initialize=params.capex_var_NGB)  # $/MW
    m.capex_var_FPC = Param(initialize=params.capex_var_FPC)  # $/MW
    m.capex_var_TES = Param(initialize=params.capex_var_TES)  # $/MWh
    m.capex_var_TES_diff = Param(initialize=params.capex_var_TES_diff)  # $/MW
    
    m.price_energy = Param(m.T, mutable=True, initialize=params.price_energy)  # $/MWh
    m.price_demand = Param(mutable=True, initialize=params.price_demand)  # $/kW
    m.price_NG = Param(mutable=True, initialize=params.price_NG)  # $/MWh
    
    m.heating_demand_MWh = Param(m.T, mutable=True, initialize=params.heating_demand_MWh)  # MW or MWh
    m.FPC_generation_MWh = Param(m.T, mutable=True, initialize=params.FPC_generation_MWh)  # MW or MWh
    
    m.COP_IHP = Param(mutable=True, initialize=params.COP_IHP)
    
    m.SOC_TES_i = Param(mutable=True, initialize=params.SOC_TES_i)
    
    m.carbon_offset_price = Param(mutable=True, initialize=params.carbon_offset_price)
    m.emission_factor = Param(mutable=True, initialize=params.emission_factor)

    return m


def add_decision_variables(m):

    # objective function
    m.total_cost = Var()
    
    # capital costs
    m.capex = Var(within=NonNegativeReals)
    m.capex_IHP = Var(within=NonNegativeReals)
    m.capex_TES = Var(within=NonNegativeReals)
    m.capex_NGB = Var(within=NonNegativeReals)
    m.capex_FPC = Var(within=NonNegativeReals)
    
    # operating costs
    m.opex = Var(within=NonNegativeReals)
    m.opex_annual = Var(within=NonNegativeReals)
    m.opex_hourly = Var(m.T, within=NonNegativeReals)
    m.opex_IHP = Var(m.T, within=NonNegativeReals)
    m.opex_IHP_peak = Var(m.M, within=NonNegativeReals)
    m.opex_NGB = Var(m.T, within=NonNegativeReals)

    # emission costs
    m.emission_cost_hourly = Var(m.T, within=NonNegativeReals)

    # heat pump
    m.Q_IHP = Var(m.T, within=NonNegativeReals)
    m.Q_IHP_max = Var(within=NonNegativeReals)
    m.W_IHP = Var(m.T, within=NonNegativeReals)
    m.W_IHP_monthly_max = Var(m.M, within=NonNegativeReals)
    
    # FPC
    m.Q_FPC = Var(m.T, within=NonNegativeReals)
    m.A_FPC = Var(within=NonNegativeReals)
    m.Q_FPC_max = Var(within=NonNegativeReals)
    
    # TES
    m.Q_TES = Var(m.T, within=NonNegativeReals)
    m.Q_TES_max = Var(within=NonNegativeReals)
    m.Q_TES_diff_pos = Var(m.T, within=NonNegativeReals)
    m.Q_TES_diff_neg = Var(m.T, within=NonNegativeReals)
    m.Q_TES_diff_max = Var(within=NonNegativeReals)
    # m.V_TES = Var(within=NonNegativeReals)
    
    # Boiler
    m.Q_NGB = Var(m.T, within=NonNegativeReals)
    m.Q_NGB_max = Var(within=NonNegativeReals)

    return m


def add_constraints(m):

    # objective function
    def objective_rule(m):
        return m.total_cost
    m.objective_function = Objective(rule=objective_rule, sense=minimize)

    ''' Total Cost '''

    def total_cost_rule(m):
        return m.total_cost == m.capex + m.opex
    m.total_cost_constraint = Constraint(rule=total_cost_rule)

    ''' Capital Cost '''

    # capital cost: total
    def capex_rule(m):
        return m.capex == m.capex_IHP + m.capex_TES + m.capex_NGB + m.capex_FPC
    m.capex_constraint = Constraint(rule=capex_rule)

    # capital cost: IHP
    def capex_IHP_rule(m):
        return m.capex_IHP == m.capex_var_IHP * m.Q_IHP_max
    m.capex_IHP_constraint = Constraint(rule=capex_IHP_rule)

    # capital cost: TES
    def capex_TES_rule(m):
        return m.capex_TES == m.capex_var_TES * m.Q_TES_max + m.capex_var_TES_diff * m.Q_TES_diff_max
        # return m.capex_TES == m.capex_var_TES * (m.V_TES*m.rho*m.Cp*m.dT*m.kJ_to_MWh)  # energetic cost
    m.capex_TES_constraint = Constraint(rule=capex_TES_rule)

    # capital cost: NGB
    def capex_NGB_rule(m):
        return m.capex_NGB == m.capex_var_NGB * m.Q_NGB_max
    m.capex_NGB_constraint = Constraint(rule=capex_NGB_rule)

    # capital cost: FPC
    def capex_FPC_rule(m):
#         return m.capex_FPC == capex_var_FPC * m.A_FPC + capex_fix_FPC * m.y_FPC
        return m.capex_FPC == m.capex_var_FPC*m.Q_FPC_max
    
    m.capex_FPC_constraint = Constraint(rule=capex_FPC_rule)

    ''' Operating Cost '''

    def opex_rule(m):
        return m.opex == sum( m.opex_annual / ((1+0.03)**(y+1)) for y in range(25) )
    m.opex_constraint = Constraint(rule=opex_rule)

    def opex_annual_rule(m):
        return m.opex_annual == sum(m.opex_hourly[t] for t in m.T) + sum(m.opex_IHP_peak[month] for month in m.M)
    m.opex_annual_constraint = Constraint(rule=opex_annual_rule)

    # hourly OPEX
    def opex_hourly_rule(m, t):
        return m.opex_hourly[t] == m.opex_IHP[t] + m.opex_NGB[t]
    m.opex_hourly_constraint = Constraint(m.T, rule=opex_hourly_rule)

    # IHP OPEX: energy
    def opex_IHP_rule(m, t):
        return m.opex_IHP[t] == m.W_IHP[t]*m.price_energy[t]
    m.opex_IHP_constraint = Constraint(m.T, rule=opex_IHP_rule)

    # IHP OPEX: peak demand charges
#     print(price_demand)
    def opex_IHP_peak_rule(m, month):
        return m.opex_IHP_peak[month] == m.price_demand*m.W_IHP_monthly_max[month]
    m.opex_IHP_peak_constraint = Constraint(m.M, rule=opex_IHP_peak_rule)

    # NGB OPEX
    def opex_NGB_rule(m, t):
        return m.opex_NGB[t]== m.price_NG*m.Q_NGB[t] + m.emission_cost_hourly[t]
    m.opex_NGB_constraint = Constraint(m.T, rule=opex_NGB_rule)

    ''' Emission Cost '''

    def emission_cost_rule(m, t):
        return m.emission_cost_hourly[t] == m.carbon_offset_price*m.emission_factor*m.Q_NGB[t]
    m.emission_cost_constraint = Constraint(m.T, rule=emission_cost_rule)

    ''' Heat Balance '''

    # heat balance: TES time step is defined at the end of the interval 
    def energy_balance_rule(m, t):
        if t > 0:
            return m.Q_TES[t] - m.Q_TES[t-1] == m.Q_IHP[t] + m.Q_NGB[t] + m.Q_FPC[t] - m.heating_demand_MWh[t]
        else:
            return m.Q_TES[t] - m.SOC_TES_i*m.Q_TES_max == m.Q_IHP[t] + m.Q_NGB[t] + m.Q_FPC[t] - m.heating_demand_MWh[t]
    m.energy_balance_constraint = Constraint(m.T, rule=energy_balance_rule)

    ''' Storage Difference '''
    
    def storage_diff_rule(m, t):
        if t > 0:
            return m.Q_TES[t] - m.Q_TES[t-1] == m.Q_TES_diff_pos[t] - m.Q_TES_diff_neg[t]
        else:
            return m.Q_TES[t] - m.SOC_TES_i*m.Q_TES_max == m.Q_TES_diff_pos[t] - m.Q_TES_diff_neg[t]
    m.storage_diff_constraint = Constraint(m.T, rule=storage_diff_rule)

    def storage_diff_max_pos_rule(m, t):
        return m.Q_TES_diff_max >= m.Q_TES_diff_pos[t]
    m.storage_diff_max_pos_constraint = Constraint(m.T, rule=storage_diff_max_pos_rule)

    def storage_diff_max_neg_rule(m, t):
        return m.Q_TES_diff_max >= m.Q_TES_diff_neg[t]
    m.storage_diff_max_neg_constraint = Constraint(m.T, rule=storage_diff_max_neg_rule)
        
    ''' Storage Initial Level '''

    # storage initial level: need to set to zero, otherwise it treats it as free energy and over sizes the storage
    def storage_initial_rule(m):
        return m.Q_TES[0] == 0
        # return m.Q_TES[0] == m.Q_TES_max*0.5
    m.storage_initial_constraint = Constraint(rule=storage_initial_rule)

    ''' Upper Bounds '''

    # TES upper bound
    def storage_upper_rule(m, t):
        return m.Q_TES[t] <= m.Q_TES_max
        # return m.Q_TES[t] <= m.V_TES*m.rho*m.Cp*m.dT*m.kJ_to_MWh
    m.storage_upper_constraint = Constraint(m.T, rule=storage_upper_rule)

    # https://energyinnovation.org/wp-content/uploads/2023/07/2023-07-13-Industrial-Thermal-Batteries-Report-v133.pdf they say $300/kW for heat exchanger in this context
    # # TES power upper bound
    # def storage_upper_rule(m, t):
    #     return m.Q_TES[t] - m.Q_TES[t-1] <= m.Q_TES_max
    #     # return m.Q_TES[t] <= m.V_TES*m.rho*m.Cp*m.dT*m.kJ_to_MWh
    # m.storage_upper_constraint = Constraint(m.T, rule=storage_upper_rule)

    # # TES lower bound (not needed if zero)
    # def storage_lower_rule(m):
    #     return m.Q_TES[t] >= 0.05*m.Q_TES_max
    # storage_lower_constraint = Constraint(m.T, rule=storage_lower_rule)

    # IHP upper bound
    def heatpump_upper_rule(m, t):
        return m.Q_IHP[t] <= m.Q_IHP_max
    m.heatpump_upper_constraint = Constraint(m.T, rule=heatpump_upper_rule)

    # NGB upper bound
    def boiler_upper_rule(m, t):
        return m.Q_NGB[t] <= m.Q_NGB_max
    m.boiler_upper_constraint = Constraint(m.T, rule=boiler_upper_rule)

    # FPC proportional to base heating profile
    def fpc_proportion_rule(m, t):
        return m.Q_FPC[t] == m.A_FPC*m.FPC_generation_MWh[t]
    m.fpc_proportion_constraint = Constraint(m.T, rule=fpc_proportion_rule)

    # FPC upper bound
    def fpc_max_rule(m, t):
        return m.Q_FPC[t] <= m.Q_FPC_max
    m.fpc_max_constraint = Constraint(m.T, rule=fpc_max_rule)

    ''' Heat Pump Work and Monthly Peak '''

    # heat pump work
    def heatpump_work_rule(m, t):
        return m.W_IHP[t] == m.Q_IHP[t]/m.COP_IHP
    m.heatpump_work_constraint = Constraint(m.T, rule=heatpump_work_rule)

    # heat pump work monthly sum
    def heatpump_monthly_work_rule(m, month):
        ti = sum(n_days_in_each_month[0:month]*24)
        tf = sum(n_days_in_each_month[0:month+1]*24)
        m.T_month = np.arange(ti, tf)
        return sum(m.W_IHP[t] for t in m.T_month)/(n_days_in_each_month[month]*24) <= m.W_IHP_monthly_max[month]
    m.heatpump_monthly_work_constraint = Constraint(m.M, rule=heatpump_monthly_work_rule)

    return m


def run_optimization(params, print_flag=True, solver='amplxpress', save=False):
    
    ### build model
    m = create_model()
    m = add_params(m, params)
    m = add_decision_variables(m)
    m = add_constraints(m)

    ### solve model
    try:
        solver = SolverFactory('gurobi')
    except:
        pass
    try:
        solver = SolverFactory('amplxpress')
    except:
        pass
    try:
        solver = SolverFactory('cbc')
    except:
        print("No solver found. Please install 'gurobi', 'amplxpress', or 'cbc' and try again.")
    
    res = solver.solve(m)
    
    if print_flag:
        print('Optimization Finished Successfully')

    ### Save model and results

    # assign results 
    results = Results(m)

    # save model and results
    os.makedirs(FILE_PATH.parent / 'results', exist_ok=True)
    
    if save:

        current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        # save model
        with open(FILE_PATH.parent / ('results/model_' + current_datetime + '.pkl'), mode='wb') as file:
            cloudpickle.dump(m, file)
        
        # save results
        with open(FILE_PATH.parent / ('results/results_' + current_datetime + '.pkl'), mode='wb') as file:
            pickle.dump(results, file)

    return results
