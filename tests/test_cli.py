import json

from ukcopy.cli import main


def test_clean_file_exits_zero(tmp_path, capsys):
    f = tmp_path / "ok.md"
    f.write_text("We looked at speed, cost and quality.\n")
    assert main(["check", str(f)]) == 0


def test_issues_exit_one_and_json(tmp_path, capsys):
    f = tmp_path / "bad.md"
    f.write_text("We prioritize speed, cost, and quality!\n")
    assert main(["check", str(f), "--format", "json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert {d["rule"] for d in data} == {"us-spelling", "oxford-comma", "exclamation"}


def test_github_annotations(tmp_path, capsys):
    f = tmp_path / "bad.md"
    f.write_text("Colors.\n")
    main(["check", str(f), "--format", "github", "--no-fail"])
    assert "::warning file=" in capsys.readouterr().out


def test_project_readme_passes_its_own_checker():
    assert main(["check", "README.md"]) == 0
