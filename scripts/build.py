"""Build Jupyter Book 2 + JupyterLite + web into one GitHub Pages artifact."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def run(args,cwd=ROOT,env=None):
    print('+ '+' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),cwd=cwd,env=env,check=True)


def safe_clear(path):
    path=path.resolve()
    if not path.is_relative_to(ROOT) or path==ROOT:
        raise ValueError('Build cleanup must remain under repository root')
    if path.exists(): shutil.rmtree(path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base-url',default='/JupyterLite-Climate-and-Health',help='GitHub Pages prefix; empty for root local preview')
    parser.add_argument('--skip-notebooks',action='store_true',help='Use existing executed outputs; CI must not skip notebook verification')
    args=parser.parse_args()
    env=os.environ.copy()
    env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
    env['PYTHONUTF8']='1'
    run([sys.executable,'scripts/prepare_data.py'],env=env)
    run([sys.executable,'scripts/make_projects.py'],env=env)
    if not args.skip_notebooks:run([sys.executable,'scripts/check_notebooks.py'],env=env)
    book=ROOT/'book';shutil.copytree(ROOT/'content/notebooks',book/'notebooks',dirs_exist_ok=True)
    # Strip only execution paths from tracebacks? None: failed notebook execution aborts above.
    env['BASE_URL']=args.base_url.rstrip('/')+'/book'
    jupyter=shutil.which('jupyter',path=env['PATH'])
    if not jupyter:raise RuntimeError('Activate the pinned build environment; jupyter is missing')
    run([jupyter,'book','build','--html','--strict'],cwd=book,env=env)
    site=ROOT/'_site';safe_clear(site);site.mkdir()
    shutil.copytree(ROOT/'web',site,dirs_exist_ok=True)
    shutil.copytree(ROOT/'assets',site/'assets',dirs_exist_ok=True)
    shutil.copytree(ROOT/'content/data',site/'data',dirs_exist_ok=True)
    shutil.copytree(ROOT/'content/projects',site/'projects',dirs_exist_ok=True)
    shutil.copytree(book/'_build/html',site/'book',dirs_exist_ok=True)
    run([jupyter,'lite','build','--contents','content','--output-dir',str(site/'lite')],env=env)
    (site/'.nojekyll').write_text('')
    (site/'build-info.json').write_text(json.dumps({'book':'Jupyter Book 2.1.7','base_url':args.base_url,'runtime':'JupyterLite 0.8.6 / jupyterlite-pyodide-kernel 0.8.6','commit':os.getenv('GITHUB_SHA','local'),'data_contract':'observations and synthetic scenarios are separate'},indent=2))
    # MyST exports extensionless routes as .html files; create directory aliases for portable links.
    for page in (site/'book').glob('*.html'):
        if page.stem not in ('index','404'):
            alias=site/'book'/page.stem/'index.html';alias.parent.mkdir(exist_ok=True)
            # MyST asset references use BASE_URL, so directory aliases preserve their resolution.
            shutil.copy2(page,alias)
    run([sys.executable,'scripts/check_site.py'],env=env)
    print(f'Built {site}; preview under {args.base_url or "/"}')


if __name__=='__main__':main()
