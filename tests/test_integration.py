from pathlib import Path

from click.testing import CliRunner

from fvcs.main import main


def test_nominal_simple():
    runner = CliRunner()
    with runner.isolated_filesystem():
        temp_dir = Path.cwd()

        with open("file.txt", "w") as f:
            f.write("first\n")

        result = runner.invoke(main, ["init"])
        assert result.exit_code == 0
        assert result.output == f"The repository is initialized in {temp_dir}\n"
        assert Path(".fvcs").is_dir()

        result = runner.invoke(main, ["init"])
        assert result.exit_code == 2
        assert result.output == f"The repository already exists in {temp_dir}\n"

        result = runner.invoke(main, ["add", "file.txt"])
        assert result.exit_code == 0
        assert result.output == "Added file.txt to the repository\n"
        latest = Path(".fvcs/tree/file.txt/latest")
        assert latest.is_file()
        assert latest.read_text() == "first\n"
        diffs = Path(".fvcs/tree/file.txt/versions")
        assert diffs.is_dir()
        assert list(diffs.iterdir()) == []

        result = runner.invoke(main, ["add", "file.txt"])
        assert result.exit_code == 2
        assert result.output == "file.txt is already in the repository\n"

        result = runner.invoke(main, ["diff", "file.txt"])
        assert result.exit_code == 0
        assert result.output == "file.txt is not modified\n"

        with open("file.txt", "a") as f:
            f.write("second\n")

        result = runner.invoke(main, ["diff", "file.txt"])
        assert result.exit_code == 0
        diff = "--- file.txt\n+++ file.txt\n@@ -1 +1,2 @@\n first\n+second\n\n"
        assert result.output == diff

        result = runner.invoke(main, ["update", "file.txt"])
        assert result.exit_code == 0
        assert result.output == "Updated file.txt (previous version: 1)\n"
        latest = Path(".fvcs/tree/file.txt/latest")
        assert latest.is_file()
        assert latest.read_text() == "first\nsecond\n"
        diffs = Path(".fvcs/tree/file.txt/versions")
        assert diffs.is_dir()
        diff_path = Path(".fvcs/tree/file.txt/versions/1.diff")
        assert diff_path.is_file()
        diff = "--- file.txt\n+++ file.txt\n@@ -1,2 +1 @@\n first\n-second\n"
        assert diff_path.read_text() == diff

        result = runner.invoke(main, ["update", "file.txt"])
        assert result.exit_code == 2
        assert result.output == "file.txt is not modified\n"

        result = runner.invoke(main, ["get", "file.txt", "1"])
        assert result.exit_code == 0
        assert result.output == "Restored file.txt to version 1\n"
        assert Path("file.txt").read_text() == "first\n"
        latest = Path(".fvcs/tree/file.txt/latest")
        assert latest.is_file()
        assert latest.read_text() == "first\nsecond\n"
        diff_path = Path(".fvcs/tree/file.txt/versions/1.diff")
        assert diff_path.is_file()

        with open("file.txt", "a") as f:
            f.write("foo\n")
        assert Path("file.txt").read_text() == "first\nfoo\n"

        result = runner.invoke(main, ["get", "file.txt", "1"])
        assert result.exit_code == 3
        assert result.output == "file.txt is modified\n"
        assert Path("file.txt").read_text() == "first\nfoo\n"

        result = runner.invoke(main, ["get", "--force", "file.txt", "1"])
        assert result.exit_code == 0
        assert result.output == "Restored file.txt to version 1\n"
        assert Path("file.txt").read_text() == "first\n"

        # FIXME: should be restoring to latest, if want to test redundant operations
        #        (otherwise, there is always a diff)
        # TODO: actually implement the ability to restore to latest
        # result = runner.invoke(main, ["get", "file.txt", "1"])
        # assert result.exit_code == 3
        # assert result.output == "Restored file.txt to version 1\n"
        # assert Path("file.txt").read_text() == "first\n"
