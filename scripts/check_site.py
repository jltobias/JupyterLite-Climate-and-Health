"""Check authored local links and required static products under a repository prefix."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'_site'
PREFIX='/JupyterLite-Climate-and-Health'


class Links(HTMLParser):
    def __init__(self):super().__init__();self.values=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('href','src') and value:self.values.append(value)


def main():
    for name in ['index.html','book/index.html','lite/lab/index.html','explore/index.html','data/cases.json','projects/climate-health.jGIS']:
        if not (SITE/name).is_file():raise AssertionError(f'Missing product {name}')
    errors=[]
    # Generated Book/Lab internals are handled by their builders; inspect every authored HTML page.
    pages=[SITE/p.relative_to(ROOT/'web') for p in (ROOT/'web').rglob('*.html')]
    for path in pages:
        parser=Links();parser.feed(path.read_text(encoding='utf-8'))
        for value in parser.values:
            parsed=urlsplit(value)
            if parsed.scheme or parsed.netloc or not parsed.path:continue
            target=(SITE/parsed.path[len(PREFIX):].lstrip('/') if parsed.path.startswith(PREFIX+'/') else SITE/parsed.path.lstrip('/') if parsed.path.startswith('/') else path.parent/unquote(parsed.path)).resolve()
            if not target.is_relative_to(SITE.resolve()):errors.append(f'{path.name}: escapes site: {value}')
            elif not target.exists() and not target.with_suffix('.html').exists():errors.append(f'{path.name}: missing {value}')
    if errors:raise AssertionError('\n'.join(errors))
    print(f'Validated products and local links in {len(pages)} authored HTML pages')


if __name__=='__main__':main()
