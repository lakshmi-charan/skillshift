import shlex


def rsync_command(sources, host, dest):
    args = ["rsync", "-az"] + list(sources) + ["%s:%s" % (host, dest)]
    return " ".join(shlex.quote(a) for a in args)
