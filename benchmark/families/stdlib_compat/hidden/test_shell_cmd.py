import shlex
import subprocess

from sa_testlib import case, need

TRICKY = ["plain", "two words", "it's", "$HOME", "semi;colon", "", "back\\slash", 'dq"x', "*.txt", "naïve", "a\nb"]


def _sh_argv(cmdline):
    out = subprocess.run(["/bin/sh", "-c", "printf '%s\\0' " + cmdline], capture_output=True, check=True).stdout
    return out.decode("utf-8").split("\0")[:-1]


@case("quote_arg")
def h_quote_roundtrip(mod):
    q = need(mod, "quote_arg")
    for s in TRICKY:
        assert shlex.split(q(s)) == [s], s


@case("quote_arg")
def h_quote_safe_unchanged(mod):
    q = need(mod, "quote_arg")
    assert q("simple-name_1.txt") == "simple-name_1.txt"
    assert q("") == "''"


@case("quote_arg")
def h_quote_real_shell(mod):
    q = need(mod, "quote_arg")
    for s in TRICKY:
        if s == "":
            continue
        assert _sh_argv(q(s)) == [s], s


@case("join_command")
def h_join(mod):
    j = need(mod, "join_command")
    args = ["grep", "-r", "hello world", "it's", "$PATH", 42]
    line = j(args)
    assert shlex.split(line) == ["grep", "-r", "hello world", "it's", "$PATH", "42"]
    assert _sh_argv(line) == ["grep", "-r", "hello world", "it's", "$PATH", "42"]


@case("join_command")
def h_join_simple(mod):
    assert need(mod, "join_command")(["ls", "-la", "/tmp"]) == "ls -la /tmp"


@case("remote_command")
def h_remote(mod):
    r = need(mod, "remote_command")
    args = ["cat", "my file.txt", "it's"]
    parts = shlex.split(r("db1.internal", args, user="deploy"))
    assert parts[:2] == ["ssh", "deploy@db1.internal"] and len(parts) == 3
    assert shlex.split(parts[2]) == args


@case("remote_command")
def h_remote_nouser(mod):
    parts = shlex.split(need(mod, "remote_command")("web-2", ["echo", "$HOME"]))
    assert parts[:2] == ["ssh", "web-2"] and shlex.split(parts[2]) == ["echo", "$HOME"]


@case("split_command")
def h_split(mod):
    s = need(mod, "split_command")
    assert s("cp 'a b.txt' \"c d.txt\" e") == ["cp", "a b.txt", "c d.txt", "e"]
    assert s("") == []
