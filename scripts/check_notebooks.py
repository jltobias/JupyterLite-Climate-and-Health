"""Execute each core notebook in a fresh kernel against an isolated portable content tree."""
from pathlib import Path
import shutil
import tempfile
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]


def main():
    notebooks=sorted((ROOT/'content/notebooks').glob('*.ipynb'))
    if len(notebooks)<12: raise RuntimeError('At least 12 substantive notebooks required')
    for path in notebooks:
        with tempfile.TemporaryDirectory(prefix='climate-lesson-') as temporary:
            content=Path(temporary)/'content'
            shutil.copytree(ROOT/'content',content,ignore=shutil.ignore_patterns('__pycache__'))
            nb=nbformat.read(path,as_version=4)
            nbformat.validate(nb)
            NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(content/'notebooks')}}).execute()
            if any(out.output_type=='error' for c in nb.cells if c.cell_type=='code' for out in c.get('outputs',[])):
                raise RuntimeError(f'Notebook produced an error: {path.name}')
            nbformat.write(nb,path)
            print(f'PASS {path.name}',flush=True)
    print(f'Executed {len(notebooks)} notebooks in fresh kernels')


if __name__=='__main__':main()
