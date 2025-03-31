import os
import re
import numpy as np
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
from patsy import dmatrix
from stargazer.stargazer import Stargazer, LineLocation

class StatewiseAnalysis:
    """
    A class to perform statewise analysis on residential consumption data.
    
    Attributes:
    data_dir (str): Directory containing the raw data files.
    output_dir (str): Directory to save the output files.
    states (list or None): List of states to analyze, or None to analyze all states.
    deg_free (int): The degrees of freedom for the natural splines (default is 5).
    
    Methods:
    _create_output_dirs(): Creates the output directories if they do not exist.
    _load_data(): Loads the data from the specified directory and applies necessary transformations.
    generate_summary_stats(): Generates summary statistics for each state and saves to CSV.
    _apply_splines(df, column): Applies natural cubic splines to a given column in the dataframe.
    run_regressions(): Runs OLS regressions for each state and saves the results in LaTeX format.
    plot_results(results): Plots the results of the regressions for each state.
    run(): Executes the full analysis including generating summary stats, running regressions, and plotting.
    """
    
    def __init__(self, data_dir, output_dir, deg_free_long, deg_free_short, states=None):
        """
        Initializes the StatewiseAnalysis class.
        
        Parameters:
        data_dir (str): Path to the directory containing raw data.
        output_dir (str): Path to the directory where output files will be saved.
        states (list, optional): List of states to analyze. If None, all states are analyzed.
        deg_free_long (int, optional): Degrees of freedom for long-run natural splines.
        deg_free_short (int, optional): Degrees of freedom for short-run natural splines.
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.deg_free_short = int(deg_free_short)
        self.deg_free_long = int(deg_free_long)
        self.states = states
        self._create_output_dirs()
        self.df = self._load_data()
    
    def _create_output_dirs(self):
        """
        Creates the necessary output directories for saving results.
        Ensures the regression outputs and plots directories are created.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'regression_outputs'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'plots'), exist_ok=True)
    
    def _load_data(self):
        """
        Loads and processes the data from the specified directory.
        
        This function reads all CSV files in the data directory, concatenates them,
        and adds a new column 'log_residential' as the log-transformed residential consumption.
        
        Returns:
        pd.DataFrame: A concatenated DataFrame with the log-transformed residential data.
        """
        all_files = os.listdir(self.data_dir)
        all_dfs = [pd.read_csv(os.path.join(self.data_dir, file)) for file in all_files if '.csv' in file]
        df = pd.concat(all_dfs).reset_index(drop=True)
        df['log_residential'] = np.log(df['residential'])
        return df if self.states is None else df[df['state'].isin(self.states)]
    
    def generate_summary_stats(self):
        """
        Generates summary statistics for residential consumption and HDD_20 by state.
        
        The summary includes count, mean, standard deviation, min, 25%, 50%, 75%, and max.
        Saves the summary statistics as a CSV file in the output directory.
        Also generates a LaTeX table for the summary statistics and saves it as a .tex file.
        """
        # Generate summary statistics for 'residential' and 'HDD_20' by 'state'
        df_summary = self.df.groupby('state')[['residential', 'HDD_20']].describe()
        
        # Save the summary statistics as a CSV file
        summary_path = os.path.join(self.output_dir, "summary_stats.csv")
        df_summary.to_csv(summary_path)
        print(f"Summary statistics saved to {summary_path}")
        
        # LaTeX table formatting for summary statistics
        latex_table = """ 
            \\begin{table}[H]
            \\caption{Summary Statistics by State}
            \\centering
            \\resizebox{\\textwidth}{!}{
            \\begin{threeparttable}
            \\begin{tabular}{lcccccccccccc}
            \\toprule
            & \\multicolumn{8}{c}{residential} & \\multicolumn{8}{c}{HDD\_20} \\\\
            \\cmidrule(lr){2-9} \\cmidrule(lr){10-17}
            state & count & mean & std & min & 25\% & 50\% & 75\% & max & count & mean & std & min & 25\% & 50\% & 75\% & max \\\\
            \\midrule
        """
        
        # Loop through each state to add statistics to LaTeX table
        for idx, row in df_summary.iterrows():
            latex_table += f"    {idx} & " + " & ".join([f"{round(x, 2):.2f}" for x in row[0:8]]) + " & " + " & ".join([f"{round(x, 2):.2f}" for x in row[8:]]) + " \\\\ \n"
        
        latex_table += """
            \\bottomrule
            \\end{tabular}
            \\begin{tablenotes}[flushleft]
                    \\footnotesize
                    \\textit{Notes:} Summary statistics (count, mean, std, etc.) for `residential` and `HDD_20` by state.
            \\end{tablenotes}
            \\end{threeparttable}
            } 
            \\label{tab:state_summary}
        \\end{table}
        """
        
        # Save the LaTeX table to a .tex file
        latex_file_path = os.path.join(self.output_dir, 'state_summary.tex')
        with open(latex_file_path, 'w') as f:
            f.write(latex_table)
        print(f"LaTeX table with summary statistics saved to {latex_file_path}")
    
    def _apply_splines(self, df, column):
        """
        Applies natural cubic splines to a given column of a dataframe.
        
        Parameters:
        df (pd.DataFrame): The dataframe to process.
        column (str): The column to apply splines to.
        
        Returns:
        pd.DataFrame: The dataframe with the natural cubic splines added as new columns.
        list: The names of the new spline columns.
        """
        if column == 'month':
            self.deg_free = self.deg_free_short
        elif column == 'year':
            self.deg_free = self.deg_free_long

        X = df[column]
        natural_basis_mat = dmatrix(f'cr(x, df={self.deg_free}) - 1', {'x': X})
        column_names = [f'{column}_{i}' for i in range(natural_basis_mat.shape[1])]
        df_spline = pd.DataFrame(np.array(natural_basis_mat), columns=column_names)
        return pd.concat([df.reset_index(drop=True), df_spline], axis=1), column_names
    
    def run_regressions(self):
        """
        Runs OLS regressions for each state to model log_residential consumption.
        
        The regressions include:
        1. A model with natural cubic splines for year and month.
        2. A fixed effects model for year and month.
        
        The results are saved in LaTeX format in the 'regression_outputs' directory.
        
        Returns:
        dict: A dictionary containing the regression results for each state.
        """
        results = {}
        for state in self.df['state'].unique():
            # Filter the data for the current state
            df_state = self.df[self.df['state'] == state].copy()
            # Apply splines to the 'year' and 'month' columns
            df_state, ns_year_cols = self._apply_splines(df_state, 'year')
            df_state, ns_month_cols = self._apply_splines(df_state, 'month')
            
            # Define the formulas for the regressions
            formula_splines = f'log_residential ~ HDD_20 + ' + ' + '.join(ns_year_cols + ns_month_cols)
            formula_FE = 'log_residential ~ HDD_20 + C(year) + C(month)'
            
            # Run the regressions
            reg_splines = smf.ols(formula_splines, data=df_state).fit()
            reg_FE = smf.ols(formula_FE, data=df_state).fit()
            results[state] = (reg_splines, reg_FE)
            
            # Create the LaTeX table for the regression results
            stargazer = Stargazer([reg_splines, reg_FE])
            stargazer.significance_levels([1e-10000000, 1e-10000000, 1e-10000000])
            stargazer.show_degrees_of_freedom(False)
            stargazer.covariate_order(['HDD_20'])
            stargazer.add_line('Month Fixed Effects', ['', 'X'], LineLocation.FOOTER_TOP)
            stargazer.add_line('Seasonal Spline', ['X', ''], LineLocation.FOOTER_TOP)
            stargazer.add_line('Year Fixed Effects', ['', 'X'], LineLocation.FOOTER_TOP)
            stargazer.add_line('Long Run Spline', ['X', ''], LineLocation.FOOTER_TOP)
            latex_output = stargazer.render_latex()
            
            # Save the LaTeX output to a file
            with open(os.path.join(self.output_dir, 'regression_outputs', f"regression_{state}.tex"), "w") as f:
                f.write(latex_output)
        return results

    def plot_results(self, results):
        """
        Plots the regression results for each state.

        The plot includes:
        1. Actual consumption vs model predictions for both spline and fixed effects models.
        2. The year and month spline effects with the fixed effects.

        Saves the plots as a PNG file in the 'plots' directory.

        Parameters:
        results (dict): The regression results for each state.
        """

        for state, (reg_splines, reg_FE) in results.items():
            df_state = self.df[self.df['state'] == state].copy()
            df_state['year_month'] = df_state['year'].astype(str) + '-' + df_state['month'].astype(str)

            # Extract fixed effects
            intercept = reg_FE.params['Intercept']
            year_effects = {int(re.search(r'\d+', k).group()): v for k, v in reg_FE.params.items() if k.startswith('C(year)')}
            month_effects = {int(re.search(r'\d+', k).group()): v for k, v in reg_FE.params.items() if k.startswith('C(month)')}

            base_year = df_state['year'].min()
            base_month = df_state['month'].min()
            year_effects[base_year] = 0
            month_effects[base_month] = 0

            df_temp = df_state[['HDD_20', 'year', 'month']]
            df_year = df_temp.copy()

            # Create year and month spline effects
            df_year, _ = self._apply_splines(df_year, 'year')
            df_year, _ = self._apply_splines(df_year, 'month')

            df_year['HDD_20'] = 0
            df_year = df_year[df_year['month'] == df_state['month'].min()]

            df_year = df_year.drop_duplicates().sort_values('year').reset_index(drop=True)
            df_year['log_preds'] = reg_splines.predict(df_year)

            df_month = df_temp.copy()

            df_month, _ = self._apply_splines(df_month, 'month')
            df_month, _ = self._apply_splines(df_month, 'year')

            df_month['HDD_20'] = 0
            df_month = df_month[df_month['year'] == df_state['year'].min()]

            df_month = df_month.drop_duplicates().sort_values('month').reset_index(drop=True)
            df_month['log_preds'] = reg_splines.predict(df_month)

            df_year_FE = pd.DataFrame({'year': list(year_effects.keys()), 'FE_value': [intercept + v for v in year_effects.values()]})
            df_month_FE = pd.DataFrame({'month': list(month_effects.keys()), 'FE_value': [intercept + v for v in month_effects.values()]})

            # Determine plot limits
            year_y_min = min(df_year['log_preds'].min(), df_year_FE['FE_value'].min()) - 0.1
            year_y_max = max(df_year['log_preds'].max(), df_year_FE['FE_value'].max()) + 0.1
            month_y_min = min(df_month['log_preds'].min(), df_month_FE['FE_value'].min()) - 0.1
            month_y_max = max(df_month['log_preds'].max(), df_month_FE['FE_value'].max()) + 0.1

            fig, axes = plt.subplots(1, 3, figsize=(24, 6), gridspec_kw={'width_ratios': [2, 1, 1]})
            plt.rcParams['font.family'] = 'C059'
            palette = sns.color_palette("Set2")

            # Plot actual vs predicted
            sns.scatterplot(x=df_state['year_month'], y=df_state['log_residential'], ax=axes[0], color=palette[0], label='Actual Consumption')
            axes[0].plot(df_state['year_month'], reg_splines.fittedvalues, color=palette[1], label='Spline Model', linewidth=2)
            axes[0].plot(df_state['year_month'], reg_FE.fittedvalues, color=palette[2], label='Fixed Effects Model', linewidth=2)
            axes[0].set_title(f'{state} - Consumption vs Predictions', fontsize=16)
            axes[0].set_xlabel('Year-Month', fontsize=14)
            axes[0].set_ylabel('Log Residential Consumption', fontsize=14)
            axes[0].legend(fontsize=12)
            axes[0].set_xticks(df_state['year_month'][::24]) 
            axes[0].tick_params(axis='x', labelrotation=45, labelsize=12)
            axes[0].tick_params(axis='y', labelsize=12)

            # Plot year spline and fixed effects
            axes[1].plot(df_year['year'], df_year['log_preds'], label='Year Spline', color=palette[3], linewidth=2)
            axes[1].bar(df_year_FE['year'], df_year_FE['FE_value'], color='gray', alpha=0.5, label='Fixed Effects')
            axes[1].set_ylim(year_y_min, year_y_max)
            axes[1].set_title('Year Spline and Fixed Effects', fontsize=16)
            axes[1].set_xlabel('Year', fontsize=14)
            axes[1].set_ylabel('Log Residential Consumption', fontsize=14)
            axes[1].legend(fontsize=12)
            axes[1].tick_params(axis='both', labelsize=12)

            # Plot month spline and fixed effects
            axes[2].plot(df_month['month'], df_month['log_preds'], label='Month Spline', color=palette[5], linewidth=2)
            axes[2].bar(df_month_FE['month'], df_month_FE['FE_value'], color='gray', alpha=0.5, label='Fixed Effects')
            axes[2].set_ylim(month_y_min, month_y_max)
            axes[2].set_title('Month Spline and Fixed Effects', fontsize=16)
            axes[2].set_xlabel('Month', fontsize=14)
            axes[2].set_ylabel('Log Residential Consumption', fontsize=14)
            axes[2].legend(fontsize=12)
            axes[2].tick_params(axis='both', labelsize=12)

            # Adjust the layout and save the plot
            plt.tight_layout()
            plot_path = os.path.join(self.output_dir, 'plots', f"{state}_plot.png")
            plt.savefig(plot_path)
            print(f"Plots saved to {plot_path}")

    
    def plot_comparison(self, results):
        """
        Plots the regression results for each state.
        
        The plot includes:
        1. Actual consumption vs model predictions for both spline and fixed effects models.
        2. The year and month spline with the fixed effects.
        
        Saves the plots as a PNG file in the 'plots' directory.
        
        Parameters:
        results (dict): The regression results for each state.
        """
        fig, axes = plt.subplots(len(results), 3, figsize=(24, 6 * len(results)))

        plt.rcParams['font.family'] = 'C059'
        palette = sns.color_palette("Set2")
        
        # Loop through each state and plot the results
        for i, (state, (reg_splines, reg_FE)) in enumerate(results.items()):
            df_state = self.df[self.df['state'] == state].copy()
            df_state['year_month'] = df_state['year'].astype(str) + '-' + df_state['month'].astype(str)

            # Extract fixed effects
            intercept = reg_FE.params['Intercept']
            year_effects = {int(re.search(r'\d+', k).group()): v for k, v in reg_FE.params.items() if k.startswith('C(year)')}
            month_effects = {int(re.search(r'\d+', k).group()): v for k, v in reg_FE.params.items() if k.startswith('C(month)')}

            base_year = df_state['year'].min()
            base_month = df_state['month'].min()
            year_effects[base_year] = 0
            month_effects[base_month] = 0

            df_temp = df_state[['HDD_20', 'year', 'month']]
            df_year = df_temp.copy()

           # Create year and month spline effects
            df_year, _ = self._apply_splines(df_year, 'year')
            df_year, _ = self._apply_splines(df_year, 'month')

            df_year['HDD_20'] = 0
            df_year = df_year[df_year['month'] == df_state['month'].min()]

            df_year = df_year.drop_duplicates().sort_values('year').reset_index(drop=True)
            df_year['log_preds'] = reg_splines.predict(df_year)

            df_month = df_temp.copy()

            df_month, _ = self._apply_splines(df_month, 'month')
            df_month, _ = self._apply_splines(df_month, 'year')

            df_month['HDD_20'] = 0
            df_month = df_month[df_month['year'] == df_state['year'].min()]

            df_month = df_month.drop_duplicates().sort_values('month').reset_index(drop=True)
            df_month['log_preds'] = reg_splines.predict(df_month)

            df_year_FE = pd.DataFrame({'year': list(year_effects.keys()), 'FE_value': [intercept + v for v in year_effects.values()]})
            df_month_FE = pd.DataFrame({'month': list(month_effects.keys()), 'FE_value': [intercept + v for v in month_effects.values()]})

            # Determine plot limits
            year_y_min = min(df_year['log_preds'].min(), df_year_FE['FE_value'].min()) - 0.1
            year_y_max = max(df_year['log_preds'].max(), df_year_FE['FE_value'].max()) + 0.1
            month_y_min = min(df_month['log_preds'].min(), df_month_FE['FE_value'].min()) - 0.1
            month_y_max = max(df_month['log_preds'].max(), df_month_FE['FE_value'].max()) + 0.1

            # Plot actual vs predicted
            sns.scatterplot(x=df_state['year_month'], y=df_state['log_residential'], ax=axes[i, 0], color=palette[0], label='Actual Consumption')
            axes[i, 0].plot(df_state['year_month'], reg_splines.fittedvalues, color=palette[1], label='Spline Model', linewidth=2)
            axes[i, 0].plot(df_state['year_month'], reg_FE.fittedvalues, color=palette[2], label='Fixed Effects Model', linewidth=2)
            axes[i, 0].set_title(f'{state} - Consumption vs Predictions', fontsize=16)
            axes[i, 0].set_xlabel('Year-Month', fontsize=14)
            axes[i, 0].set_ylabel('Log Residential Consumption', fontsize=14)
            axes[i, 0].legend(fontsize=12)
            axes[i, 0].set_xticks(df_state['year_month'][::24]) 
            axes[i, 0].tick_params(axis='x', labelrotation=45, labelsize=12)
            axes[i, 0].tick_params(axis='y', labelsize=12)

            # Plot year spline and fixed effects
            axes[i, 1].plot(df_year['year'], df_year['log_preds'], label='Year Spline', color=palette[3], linewidth=2)
            axes[i, 1].bar(df_year_FE['year'], df_year_FE['FE_value'], color='gray', alpha=0.5, label='Fixed Effects')
            axes[i, 1].set_ylim(year_y_min, year_y_max)
            axes[i, 1].set_title('Year Spline and Fixed Effects', fontsize=16)
            axes[i, 1].set_xlabel('Year', fontsize=14)
            axes[i, 1].set_ylabel('Log Residential Consumption', fontsize=14)
            axes[i, 1].legend(fontsize=12)
            axes[i, 1].tick_params(axis='both', labelsize=12)

            # Plot month spline and fixed effects
            axes[i, 2].plot(df_month['month'], df_month['log_preds'], label='Month Spline', color=palette[5], linewidth=2)
            axes[i, 2].bar(df_month_FE['month'], df_month_FE['FE_value'], color='gray', alpha=0.5, label='Fixed Effects')
            axes[i, 2].set_ylim(month_y_min, month_y_max)
            axes[i, 2].set_title('Month Spline and Fixed Effects', fontsize=16)
            axes[i, 2].set_xlabel('Month', fontsize=14)
            axes[i, 2].set_ylabel('Log Residential Consumption', fontsize=14)
            axes[i, 2].legend(fontsize=12)
            axes[i, 2].tick_params(axis='both', labelsize=12)
        
        # Adjust the layout and save the plot
        plt.tight_layout()
        plot_path = os.path.join(self.output_dir, 'plots', "statewise_plots.png")
        plt.savefig(plot_path)
        print(f"Plots saved to {plot_path}")

    def run(self):
        """
        Executes the full analysis.
        
        This method runs the following steps:
        1. Generate summary statistics for each state.
        2. Run regressions for each state.
        3. Plot the regression results.
        """
        self.generate_summary_stats()
        results = self.run_regressions()
        self.plot_results(results)
        self.plot_comparison(results)

if __name__ == "__main__":
    import argparse
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Run Statewise Analysis")
    parser.add_argument("data_dir", type=str, help="Path to the data directory")
    parser.add_argument("output_dir", type=str, help="Path to the output directory")
    parser.add_argument("deg_free_long", type=str, help="Num of degrees of freedom for long-run natural splines")
    parser.add_argument("deg_free_short", type=str, help="Num of degrees of freedom for short-run natural splines")
    parser.add_argument("--states", nargs="*", help="List of states to analyze", default=None)
    args = parser.parse_args()
    
    # Create the analysis object and run the analysis
    analysis = StatewiseAnalysis(data_dir=args.data_dir, output_dir=args.output_dir, deg_free_long=args.deg_free_long, deg_free_short=args.deg_free_short, states=args.states)
    analysis.run()
