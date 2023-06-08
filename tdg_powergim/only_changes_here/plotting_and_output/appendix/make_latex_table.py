import pandas as pd


def make_latex_for_appendix(csv_file, output_tex_path, caption, label):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Get the column names from the CSV file
    column_names = df.columns.tolist()

    # Convert column names to LaTeX format
    header = [r'\textbf{' + name.replace('_', ' ') + '}' for name in column_names]

    # Generate LaTeX table
    table = df.to_latex(header=header, bold_rows=True, escape=False)

    # Construct the complete LaTeX table
    complete_table = '\\begin{table}\n' + \
                     '    \\centering\n' + \
                     f'    \\caption{{{caption}}}\n' + \
                     f'    \\label{{{label}}}\n' + \
                     table + \
                     '\\end{table}\n'

    # Write the LaTeX table to the output file
    with open(output_tex_path, 'w') as f:
        f.write(complete_table)


# Generators for DE
# make_latex_for_appendix('/Users/tobiassjoli/Documents/GitHub/powergim/only_changes_here/make_input_data/generation/generators_DE_new.csv',
                        '/Users/tobiassjoli/Documents/Master/Appendix/generators_latex.tex',
                        'Generators for DE', 'app: generators_DE')

