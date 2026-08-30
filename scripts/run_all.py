"""Orchestrate the full pipeline:
- generate dataset (optional)
- clean data
- run analysis
- generate charts
- train ML model

Usage:
    python scripts/run_all.py --rows 1000 --generate --load-db
"""
import argparse
import subprocess
import sys
import os


def run_cmd(cmd, check=True):
    print('>',' '.join(cmd))
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print('ERROR:', res.stderr, file=sys.stderr)
        if check:
            raise RuntimeError(f'Command failed: {cmd}')
    return res


def main(rows=1000, generate=False, load_db=False):
    project_root = os.path.dirname(os.path.dirname(__file__))

    # 1. Generate dataset
    if generate:
        run_cmd([sys.executable, os.path.join(project_root, 'scripts', 'generate_dataset.py'), '--rows', str(rows), '--out', os.path.join('data','raw_sales.csv')])

    # 2. Clean data
    cmd = [sys.executable, '-m', 'src.cleaning', '--input', os.path.join('data','raw_sales.csv'), '--out', os.path.join('data','cleaned_sales.csv')]
    if load_db:
        cmd.append('--load-db')
    run_cmd(cmd)

    # 3. Analysis
    run_cmd([sys.executable, os.path.join(project_root, 'scripts', 'run_analysis.py'), '--input', os.path.join('data','cleaned_sales.csv'), '--out', os.path.join('data','analysis')])

    # 4. Charts
    run_cmd([sys.executable, os.path.join(project_root, 'scripts', 'generate_charts.py'), '--input', os.path.join('data','cleaned_sales.csv'), '--out', os.path.join('static','images')])

    # 5. Train model
    run_cmd([sys.executable, os.path.join(project_root, 'scripts', 'train_model.py'), '--input', os.path.join('data','cleaned_sales.csv'), '--model', os.path.join('models','sales_model.pkl')])

    print('\nPipeline completed successfully.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', type=int, default=1000)
    parser.add_argument('--generate', action='store_true', help='Generate a raw dataset first')
    parser.add_argument('--load-db', action='store_true', help='Load cleaned data into DB during cleaning step')
    args = parser.parse_args()
    main(rows=args.rows, generate=args.generate, load_db=args.load_db)
