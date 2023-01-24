import subprocess
import os
import pwd
from decouple import config

REPOSITORY: str = str(
    config(
        "HTTP_NODE_URL",
        cast=str,
        default="https://01.wg-test.freifunk-aachen.de/data/nodes.json",
    )
)


def _demote(user_uid, user_gid):
    def result():
        print("{}:{}".format(user_uid, user_gid))
        os.setgid(user_gid)
        os.setuid(user_uid)

    return result


def _execute_autouser(cmd) -> None:
    # WARNING this is NOT threadsafe.
    autouser = "auto"
    pw_record = pwd.getpwnam(autouser)
    homedir = pw_record.pw_dir
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid
    env = os.environ.copy()
    env.update({"HOME": homedir, "LOGNAME": autouser, "USER": autouser})

    s = subprocess.Popen(
        [cmd],
        shell=True,
        env=env,
        preexec_fn=_demote(user_uid, user_gid),
        stdout=subprocess.PIPE,
    )
    s.wait()


def push() -> None:
    _execute_autouser(f"git -C {REPOSITORY} push")


def pull() -> None:
    _execute_autouser(f"git -C {REPOSITORY} pull")


def commit(filename: str, commit_message: str) -> None:
    _execute_autouser(f"git -C {REPOSITORY} add {REPOSITORY}/{filename}")
    _execute_autouser(f'git -C {REPOSITORY} commit -m "{commit_message}')
