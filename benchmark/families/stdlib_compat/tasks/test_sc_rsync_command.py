import shlex
import subprocess

from sa_testlib import case, need


def _sh_argv(cmdline):
    out = subprocess.run(["/bin/sh", "-c", "printf '%s\\0' " + cmdline], capture_output=True, check=True).stdout
    return out.decode("utf-8").split("\0")[:-1]


@case("functional")
def t_simple(mod):
    f = need(mod, "rsync_command")
    line = f(["a.txt", "dir/"], "backup1", "/srv/data")
    assert shlex.split(line) == ["rsync", "-az", "a.txt", "dir/", "backup1:/srv/data"]


@case("functional")
def t_tricky(mod):
    f = need(mod, "rsync_command")
    srcs = ["my file.txt", "it's here", "$HOME/x", "a;rm -rf b"]
    line = f(srcs, "host", "/backups/Q1 2024")
    expect = ["rsync", "-az"] + srcs + ["host:/backups/Q1 2024"]
    assert shlex.split(line) == expect
    assert _sh_argv(line) == expect
