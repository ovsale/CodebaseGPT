from codebasegpt.code_utils import trim_code, remove_comments

def test_trim_code_consecutive_empty_lines():
    text = "Line 1\n\n\nLine 2\n\nLine 3"
    expected = "Line 1\n\nLine 2\n\nLine 3"
    assert trim_code(text) == expected

def test_trim_code_no_empty_lines():
    text = "Line 1\nLine 2\nLine 3"
    expected = "Line 1\nLine 2\nLine 3"
    assert trim_code(text) == expected

def test_trim_code_empty_lines_at_end():
    text = "Line 1\nLine 2\nLine 3\n\n\n"
    expected = "Line 1\nLine 2\nLine 3"
    assert trim_code(text) == expected


def test_remove_js_comments():
    js_content = (
        "function test() {\n"
        "// This is a comment\n"
        "    let x = 5; // Variable declaration\n"
        "/* Multi-line\n"
        "comment */\n"
        "}\n"
    )
    expected = (
        "function test() {\n"
        "    let x = 5;\n"
        "\n"
        "}" # no \n but it is ok. because trim_code will be invoked later
    )
    assert remove_comments('test.js', js_content) == expected


def test_remove_python_comments():
    py_content = (
        "def test():\n"
        "# This is a comment\n"
        "    x = 5 # Variable declaration\n"
    )
    expected = (
        "def test():\n"
        "    x = 5" # no \n but it is ok. because trim_code will be invoked later
    )
    assert remove_comments('test.py', py_content) == expected


def test_remove_html_comments():
    html_content = (
        "<html>\n"
        "<!-- This is a comment -->\n"
        "    <body></body>\n"
        "<!-- Multi-line\n"
        "comment -->\n"
        "</html>\n"
    )
    expected = (
        "<html>\n"
        "\n"
        "    <body></body>\n"
        "\n"
        "</html>\n"
    )
    assert remove_comments('test.html', html_content) == expected


def test_remove_css_comments():
    css_content = (
        "body {\n"
        "    color: red; /* This is a comment */\n"
        "/* Another\n"
        "comment */\n"
        "    background-color: blue;\n"
        "}\n"
    )
    expected = (
        "body {\n"
        "    color: red; \n"
        "\n"
        "    background-color: blue;\n"
        "}\n"
    )
    assert remove_comments('test.css', css_content) == expected

