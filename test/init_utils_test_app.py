import pathspec
from codebasegpt.init_utils import load_gitignore, list_project_files, compute_sizes, print_file_tree, get_proj_stat, print_proj_stat


def test_init_utils():
    test_TestIgnore()
    # test_tags4web()
    # test_gpt_automated_web_scraper()
    # test_tags()
    # test_auto_gen()


def test_TestIgnore():
    code_root = './test_res/TestIgnore'
    include = [
        'src/**/*',
        'package.json',
    ]
    exclude = [
        'src/test/**',
    ]

    test_any(code_root, include, exclude, True, False)


def test_tags4web():
    code_root = '../tags4web'
    include = [
        "src/**/*",
        "client/src/**/*",
        "package.json"
    ]
    exclude = [
        "src/gpt/**",
        "src/test/**",
        "client/src/test/**",
        "client/src/jest/**",
        "client/src/frontend/icons/**",
        "client/src/frontend/tiptap/icons/**"
    ]

    test_any(code_root, include, exclude, True, True)


def test_MemGPT():
    code_root = '../MemGPT'
    include = [
        "memgpt/**/*",
        "main.py",
        "README.md"
    ]
    exclude = [
    ]

    test_any(code_root, include, exclude, False, False)


def test_gpt_automated_web_scraper():
    code_root = '../gpt-automated-web-scraper'
    include = [
        "**/*",
    ]
    exclude = [
    ]

    test_any(code_root, include, exclude, True, False)


def test_tags():
    code_root = '/Users/alex/git/tags'
    include = [
        "src/java/**/*",
    ]
    exclude = [
    ]

    test_any(code_root, include, exclude, False, True)


def test_auto_gen():
    code_root = '../autogen'
    include = [
        'autogen/**/*',
        'samples/**/*',
        # 'test/**/*',
        'setup.py',
        'README.md',
    ]
    exclude = [
    ]

    test_any(code_root, include, exclude, True, False)


def test_any(code_root: str, include: list[str], exclude: list[str], gitignore: bool, remove_comments: bool):
    gitignore = pathspec.PathSpec.from_lines('gitwildmatch', [])
    if gitignore:
        gitignore = load_gitignore(code_root)

    files = list_project_files(code_root, include, exclude, gitignore)
    compute_sizes(code_root, files, remove_comments)

    print_file_tree(files)

    print()
    proj_stat = get_proj_stat(files)
    print_proj_stat(proj_stat)

