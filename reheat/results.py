import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

class Results():

    def __init__(self, m):
        
        n_t = len(m.T)  # number of time steps
        n_m = len(m.M)  # number of months
        
        # cost = m.cost.value
        self.total_cost = m.total_cost.value

        self.capex = m.capex.value
        self.capex_IHP = m.capex_IHP.value
        self.capex_TES = m.capex_TES.value
        self.capex_NGB = m.capex_NGB.value
        self.capex_FPC = m.capex_FPC.value

        self.opex = m.opex.value
        self.opex_annual = m.opex_annual.value
        self.opex_hourly = np.zeros(n_t)
        self.opex_IHP = np.zeros(n_t)
        self.opex_IHP_peak = np.zeros(n_m)
        self.opex_NGB = np.zeros(n_t)

        self.Q_IHP = np.zeros(n_t)
        self.Q_IHP_max = m.Q_IHP_max.value
        self.W_IHP = np.zeros(n_t)
        self.W_IHP_monthly_max = np.ones(n_m)

        self.Q_TES = np.zeros(n_t)
        self.Q_TES_max = m.Q_TES_max.value
        self.Q_TES_diff_max = m.Q_TES_diff_max.value

        self.Q_FPC = np.zeros(n_t)
        self.Q_FPC_max = m.Q_FPC_max.value

        self.Q_NGB = np.zeros(n_t)
        self.Q_NGB_max = m.Q_NGB_max.value

        # parameters
        self.heating_demand_MWh = np.zeros(n_t)
        self.price_energy = np.zeros(n_t)
        self.price_demand = m.price_demand.value
        self.price_NG = m.price_NG.value
        self.FPC_generation_MWh = np.zeros(n_t)
        self.COP_IHP = m.COP_IHP.value

        for t in m.T:
            self.opex_hourly[t] = m.opex_hourly[t].value
            self.opex_IHP[t] = m.opex_IHP[t].value
            self.opex_NGB[t] = m.opex_NGB[t].value
            self.Q_IHP[t] = m.Q_IHP[t].value
            self.W_IHP[t] = m.W_IHP[t].value
            self.Q_NGB[t] = m.Q_NGB[t].value
            self.Q_FPC[t] = m.Q_FPC[t].value
            self.Q_TES[t] = m.Q_TES[t].value
            self.heating_demand_MWh[t] = m.heating_demand_MWh[t].value
            self.price_energy[t] = m.price_energy[t].value
            self.FPC_generation_MWh[t] = m.FPC_generation_MWh[t].value

        for month in m.M:
            self.opex_IHP_peak[month] = m.opex_IHP_peak[month].value
            self.W_IHP_monthly_max[month] = m.W_IHP_monthly_max[month].value

        # heat pump capacity factor
        if max(self.Q_IHP) == 0:
            self.IHP_cap_fac = 0
        else:
            self.IHP_cap_fac = np.mean(self.Q_IHP)/max(self.Q_IHP)
        

    def print_results(self):

        print(f'-----------------')
        print(f'Financial Metrics')
        print(f'-----------------')

        print(f'total_cost = {self.total_cost:,.2f} $')
        print(f'capex = {self.capex:,.2f} $')
        print(f'opex = {self.opex:,.2f} $')
        print(f'capex fraction of total cost = {self.capex/self.total_cost:,.2f}')
        print(f'opex fraction of total cost = {self.opex/self.total_cost:,.2f}')

        print(f'-----------------')
        print(f'Financial Metrics by Technology')
        print(f'-----------------')

        print(f'capex_IHP = {self.capex_IHP:,.2f} $')
        print(f'capex_TES = {self.capex_TES:,.2f} $')
        print(f'capex_NGB = {self.capex_NGB:,.2f} $')
        print(f'capex_FPC = {self.capex_FPC:,.2f} $')
        print(f'annual opex = {self.opex_annual:,.2f} $/year')
        print(f'opex_IHP = {sum(self.opex_IHP):,.2f} $/year')
        print(f'opex_IHP_peak = {sum(self.opex_IHP_peak):,.2f} $/year')
        print(f'opex_NGB = {sum(self.opex_NGB):,.2f} $/year')

        print(f'-----------------')
        print(f'Heat Generation')
        print(f'-----------------')

        print(f'Q_IHP = {sum(self.Q_IHP):,.2f} MWh/year')
        print(f'Q_NGB = {sum(self.Q_NGB):,.2f} MWh/year')
        print(f'Q_FPC = {sum(self.Q_FPC):,.2f} MWh/year')

        print(f'-----------------')
        print(f'Equipment Sizing')
        print(f'-----------------')

        print(f'Q_IHP_max = {self.Q_IHP_max:,.2f} MW')
        print(f'Q_NGB_max = {self.Q_NGB_max:,.2f} MW')
        print(f'Q_FPC_max = {self.Q_FPC_max:,.2f} MW')
        print(f'Q_TES_max = {self.Q_TES_max:,.2f} MWh + {self.Q_TES_diff_max:,.2f} MW')

        print(f'-----------------')
        print(f'Electricity Metrics')
        print(f'-----------------')

        print(f'W_IHP = {sum(self.W_IHP):,.2f} MWh/year')
        print(f'W_IHP_monthly_max = {max(self.W_IHP_monthly_max):,.2f} MW (Annual Peak)')


    # plotting scheduling results for a given week
    def plot_results(self, week=1):
        
        x = np.arange((week-1)*168, week*168)
        t = x/24
        fig, axs = plt.subplots(5, 1, figsize=(10, 10), sharex=True)
        
        # external parameters: heating demand and electricity price
        i = 0; ax = axs[i]
        lns1 = ax.step(t, self.heating_demand_MWh[x], where='pre', label='demand')
        ax.set_ylabel('Demand Load\nProfile (MWh)')
        ax2 = ax.twinx()
        lns2 = ax2.step(t, self.price_energy[x]/1e3, '--r', label='price')
        ax2.set_ylabel('Electricity (Energy)\nPrice ($/kWh)')
        
        lns = lns1+lns2; labs = [l.get_label() for l in lns]; 
    #     ax2.legend(lns, labs, ncol=1, loc='center left', bbox_to_anchor=(1.07, 0.5))
        ax2.legend(lns, labs, ncol=1)

        # equipment schedule: storage
        i+=1; ax = axs[i]
        ax.step(t, self.Q_TES[x], where='pre')
        ymax = max(self.Q_TES)
        ax.set_ylim(0-0.05*ymax, ymax*1.05)
        ax.set_ylabel('Thermal Energy\nStorage (MWh)')

        # equipment schedule: heat pump 
        i+=1; ax = axs[i]
        lns1 = ax.step(t, self.Q_IHP[x], where='pre', label='heat pump')
        ymax = max(self.Q_IHP)
        if ymax > 0:
            ax.set_ylim(0-0.05*ymax, ymax*1.05)
        ax.set_ylabel('Industrial Heat\nPump (MWh)')

        # equipment schedule: solar collector
        i+=1; ax = axs[i]
        ax.step(t, self.Q_FPC[x], where='pre')
        ax.set_ylabel('Flat Plate\nCollector (MWh)')

        # equipment schedule: boiler
        i+=1; ax = axs[i]
        ax.step(t, self.Q_NGB[x], where='pre')
        ax.set_ylabel('Natural Gas\nBoiler (MWh)')

        axs[-1].xaxis.set_major_locator(ticker.MultipleLocator(1))
        axs[-1].xaxis.set_minor_locator(ticker.MultipleLocator(0.25))

        for ax in axs:
            ax.grid(alpha=0.5, which='both')

        plt.suptitle(f'Operational results for week {week}/52', fontweight='bold')
        ax.set_xlabel('Days')
        plt.tight_layout()
