import os
from codebasegpt.is_text_or_bin import is_text_file, is_text_by_enc


def test_is_text_or_bin():
    file_root = './test_res/is_text_or_bin'

    assert is_text_by_enc(os.path.join(file_root, 'test.db')) == True # wrong!
    assert is_text_file(os.path.join(file_root, 'test.db')) == False
    
    assert is_text_by_enc(os.path.join(file_root, 'app_const.cpython-312.pyc')) == True # wrong!
    assert is_text_file(os.path.join(file_root, 'app_const.cpython-312.pyc')) == False

