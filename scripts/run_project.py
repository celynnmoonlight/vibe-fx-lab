"""运行指定项目"""

import sys, os, subprocess

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'projects')


def list_projects():
    projects = []
    for d in sorted(os.listdir(PROJECTS_DIR)):
        main = os.path.join(PROJECTS_DIR, d, 'main.py')
        if os.path.isfile(main):
            projects.append(d)
    return projects


def run(name):
    main = os.path.join(PROJECTS_DIR, name, 'main.py')
    if not os.path.isfile(main):
        print(f"项目不存在: {name}")
        return
    subprocess.run([sys.executable, main], cwd=os.path.dirname(main))


if __name__ == "__main__":
    projects = list_projects()
    if len(sys.argv) < 2:
        print("可用项目:")
        for p in projects:
            print(f"  {p}")
        print(f"\n用法: python {sys.argv[0]} <项目名>")
        sys.exit(0)
    run(sys.argv[1])
