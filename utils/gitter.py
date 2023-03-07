import os
import pwd
import subprocess
from threading import Lock


class Gitter:
    def __init__(self, repo: str, clone_url: str = ""):
        self.repo = repo
        self.git_lock = Lock()

        if clone_url and not os.path.isdir(repo):
            self.clone(clone_url)

    def _demote(self, user_uid, user_gid):
        def result():
            print("{}:{}".format(user_uid, user_gid))
            os.setgid(user_gid)
            os.setuid(user_uid)

        return result

    def _execute_autouser(self, cmd) -> None:
        with self.git_lock:
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
                preexec_fn=self._demote(user_uid, user_gid),
                stdout=subprocess.PIPE,
            )
            s.wait()

    def clone(self, clone_url: str) -> None:
        self._execute_autouser(f"git clone {clone_url} {self.repo}")

    def restore(self) -> None:
        self._execute_autouser(f"git -C {self.repo} restore --staged")

    def push(self) -> None:
        self._execute_autouser(f"git -C {self.repo} push")

    def pull(self) -> None:
        self._execute_autouser(f"git -C {self.repo} pull")

    def commit(self, filename: str, commit_message: str) -> None:
        self._execute_autouser(f"git -C {self.repo} add {self.repo}/{filename}")
        self._execute_autouser(f'git -C {self.repo} commit -m "{commit_message}')

    def bulk_commit(self, filenames: list[str], commit_message: str) -> None:
        for filename in filenames:
            self._execute_autouser(f"git -C {self.repo} add {self.repo}/{filename}")
        self._execute_autouser(f'git -C {self.repo} commit -m "{commit_message}')
