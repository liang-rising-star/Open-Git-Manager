"""Git 后端操作模块"""
import subprocess
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class GitFile:
    status: str
    path: str
    old_path: Optional[str] = None
    staged: bool = False

    @property
    def status_text(self):
        return {'M':'修改','A':'新增','D':'删除','R':'重命名','?':'未跟踪','!':'忽略','C':'复制','U':'未合并'}.get(self.status, self.status)

    @property
    def status_color(self):
        from theme import STATUS_MODIFIED, STATUS_ADDED, STATUS_DELETED, STATUS_RENAMED, STATUS_UNTRACKED
        return {'M':STATUS_MODIFIED,'A':STATUS_ADDED,'D':STATUS_DELETED,'R':STATUS_RENAMED,'?':STATUS_UNTRACKED}.get(self.status,'#ccc')


@dataclass
class GitBranch:
    name: str
    is_current: bool = False
    is_remote: bool = False


class GitBackend:
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()

    def _run(self, args, timeout=30):
        try:
            r = subprocess.run(['git', '-c', 'core.quotePath=false'] + args,
                               cwd=self.repo_path, capture_output=True, text=True,
                               timeout=timeout, encoding='utf-8', errors='replace')
            return r.returncode, r.stdout, r.stderr
        except FileNotFoundError:
            return -1, "", "Git 未安装"
        except subprocess.TimeoutExpired:
            return -2, "", "超时"
        except Exception as e:
            return -3, "", str(e)

    def is_git_repo(self):
        c, o, _ = self._run(['rev-parse','--is-inside-work-tree'])
        return c == 0 and o.strip() == 'true'

    def init_repo(self):
        os.makedirs(self.repo_path, exist_ok=True)
        c, o, e = self._run(['init'])
        return c == 0, e or o

    def get_current_branch(self):
        c, o, _ = self._run(['branch','--show-current'])
        return o.strip() if c == 0 else "main"

    def get_branches(self):
        branches = []
        c, o, _ = self._run(['branch','-a'])
        if c != 0: return branches
        for line in o.strip().split('\n'):
            line = line.strip()
            if not line: continue
            cur = line.startswith('* ')
            if cur: line = line[2:]
            remote = line.startswith('remotes/')
            name = line.split(' -> ')[0] if ' -> ' in line else line
            if '...' in name: name = name.split('...')[0]
            branches.append(GitBranch(name=name, is_current=cur, is_remote=remote))
        return branches

    def get_all_info(self):
        """并行执行所有 git 查询"""
        import threading
        results = {}

        def run_cmd(key, args):
            c, o, _ = self._run(args)
            results[key] = (c, o)

        t1 = threading.Thread(target=run_cmd, args=('branch', ['branch', '--show-current']))
        t2 = threading.Thread(target=run_cmd, args=('status', ['status', '--porcelain', '-u']))
        t3 = threading.Thread(target=run_cmd, args=('remote', ['remote']))
        t1.start(); t2.start(); t3.start()
        t1.join(); t2.join(); t3.join()

        branch = results.get('branch', (0, ''))[1].strip()
        remotes = [l.strip() for l in results.get('remote', (0, ''))[1].strip().split('\n') if l.strip()]
        files = []
        c, o = results.get('status', (0, ''))
        if c == 0:
            for line in o.strip().split('\n'):
                ls = line.strip()
                if not ls or len(ls) < 3: continue
                s = ls[0]
                path = ls[3:]
                if s == ' ': continue
                staged = s in ('A', 'M', 'D', 'R', 'C')
                if s == 'R':
                    parts = path.split(' -> ', 1)
                    path = parts[-1] if len(parts) > 1 else path
                files.append(GitFile(status=s, path=path, staged=staged))

        return branch, files, remotes

    def get_changed_files(self):
        files = []
        c, o, _ = self._run(['status', '--porcelain', '-u'])
        if c == 0:
            for line in o.strip().split('\n'):
                line = line.strip()
                if not line or len(line) < 3: continue
                s = line[0]
                path = line[3:]
                if s == ' ': continue
                staged = s in ('A', 'M', 'D', 'R', 'C')
                if s == 'R':
                    parts = path.split(' -> ', 1)
                    path = parts[-1] if len(parts) > 1 else path
                files.append(GitFile(status=s, path=path, staged=staged))
        return files

    def stage_file(self, p):
        return self._run(['add', p])[0] == 0

    def unstage_file(self, p):
        return self._run(['reset','HEAD','--', p])[0] == 0

    def stage_all(self):
        return self._run(['add','.'])[0] == 0

    def unstage_all(self):
        return self._run(['reset','HEAD'])[0] == 0

    def discard_file(self, p):
        return self._run(['checkout','--', p])[0] == 0

    def discard_all(self):
        return self._run(['checkout','.'])[0] == 0

    def commit(self, msg, amend=False):
        args = ['commit','-m', msg]
        if amend: args.append('--amend')
        c, o, e = self._run(args)
        return c == 0, e or o

    def commit_all(self, msg, amend=False):
        self._run(['add','.'])
        return self.commit(msg, amend)

    def push(self, remote="origin", branch=None, force=False):
        if not branch: branch = self.get_current_branch()
        args = ['push', remote, branch]
        if force: args.insert(2,'--force')
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def pull(self, remote="origin", branch=None, rebase=False):
        if not branch: branch = self.get_current_branch()
        args = ['pull', remote, branch]
        if rebase: args.insert(2,'--rebase')
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def fetch(self, remote=None):
        args = ['fetch'] + ([remote] if remote else [])
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def create_branch(self, name, start=None):
        args = ['checkout','-b', name] + ([start] if start else [])
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def switch_branch(self, name):
        c, o, e = self._run(['checkout', name], check=False)
        return c == 0, e or o

    def delete_branch(self, name, force=False):
        c, o, e = self._run(['branch','-d' if not force else '-D', name], check=False)
        return c == 0, e or o

    def rename_branch(self, old, new):
        c, o, e = self._run(['branch','-m', old, new], check=False)
        return c == 0, e or o

    def merge(self, branch):
        c, o, e = self._run(['merge', branch], check=False)
        return c == 0, e or o

    def rebase(self, branch):
        c, o, e = self._run(['rebase', branch], check=False)
        return c == 0, e or o

    def abort_merge(self):
        return self._run(['merge','--abort'])[0] == 0

    def abort_rebase(self):
        return self._run(['rebase','--abort'])[0] == 0

    def stash(self, untracked=False):
        args = ['stash'] + (['-u'] if untracked else [])
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def stash_pop(self):
        c, o, e = self._run(['stash','pop'], check=False)
        return c == 0, e or o

    def stash_apply(self, sid=None):
        args = ['stash','apply'] + ([sid] if sid else [])
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def stash_drop(self, sid=None):
        args = ['stash','drop'] + ([sid] if sid else [])
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def stash_clear(self):
        c, o, e = self._run(['stash','clear'], check=False)
        return c == 0, e or o

    def stash_list(self):
        c, o, _ = self._run(['stash','list'])
        return o.strip().split('\n') if c == 0 and o.strip() else []

    def create_tag(self, name, msg=None):
        args = ['tag','-a', name, '-m', msg] if msg else ['tag', name]
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def delete_tag(self, name):
        c, o, e = self._run(['tag','-d', name], check=False)
        return c == 0, e or o

    def push_tags(self, remote="origin"):
        c, o, e = self._run(['push', remote,'--tags'], check=False)
        return c == 0, e or o

    def get_remotes(self):
        c, o, _ = self._run(['remote'])
        return o.strip().split('\n') if c == 0 and o.strip() else []

    def add_remote(self, name, url):
        c, o, e = self._run(['remote','add', name, url])
        return c == 0, e or o

    def remove_remote(self, name):
        c, o, e = self._run(['remote','remove', name])
        return c == 0, e or o

    def clone(self, url, target=None):
        args = ['clone', url] + ([target] if target else [])
        c, o, e = self._run(args, check=False)
        return c == 0, e or o

    def get_log(self, count=50):
        c, o, _ = self._run(['log',f'-{count}','--format=%H|%h|%an|%ad|%s','--date=short'])
        if c != 0: return []
        commits = []
        for line in o.strip().split('\n'):
            if '|' not in line: continue
            p = line.split('|', 4)
            if len(p) >= 5:
                commits.append({'hash':p[0],'short':p[1],'author':p[2],'date':p[3],'msg':p[4]})
        return commits

    def get_file_diff(self, path, staged=False):
        args = ['diff'] + (['--cached'] if staged else []) + ['--', path]
        c, o, _ = self._run(args)
        return o if c == 0 else ""

    def get_diff_stat(self):
        c, o, _ = self._run(['diff','--stat'])
        return o if c == 0 else ""

    def sync(self):
        ok, m1 = self.pull()
        if ok: ok, m2 = self.push(); return ok, m2
        return False, m1

    def open_file(self, path):
        try:
            os.startfile(os.path.join(self.repo_path, path))
            return True
        except: return False
