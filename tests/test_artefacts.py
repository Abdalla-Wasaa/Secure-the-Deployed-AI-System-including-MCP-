import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_brief():
    text=(ROOT/'manager_brief.md').read_text()
    for heading in ['Risks','Mitigations','Kenya DPA Alignment','What We Will Not Claim']: assert '## '+heading in text
    assert 'unhackable' not in text.lower()
    assert 'The system recommends rather than decides and must remain under human oversight.' in text
    for link in re.findall(r'\]\(([^)]+)\)',text): assert (ROOT/link).is_file()
def test_ignore():
    from check_gitignore import check
    assert check()==8
