"""Build shell command lines safely (for ssh, cron entries and generated scripts)."""
import pipes
import shlex


def quote_arg(arg):
    """Quote one argument so that a POSIX shell reads it back as a single word, unchanged."""
    return pipes.quote(str(arg))


def join_command(args):
    """Join an argument list into one shell command line."""
    return " ".join(pipes.quote(str(a)) for a in args)


def remote_command(host, args, user=None):
    """Command line that runs `args` on `host` via ssh; the remote shell sees the original arguments."""
    target = "%s@%s" % (user, host) if user else host
    return "ssh %s %s" % (pipes.quote(target), pipes.quote(join_command(args)))


def split_command(line):
    """Split a shell command line into its arguments."""
    return shlex.split(line)
