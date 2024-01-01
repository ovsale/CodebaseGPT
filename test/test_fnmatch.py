import fnmatch
from wcmatch import glob

def test_fnmatch():
    assert not fnmatch.fnmatch("src/Database.js", "src/**/*") 
    assert fnmatch.fnmatch("src/dir/Database.js", "src/**/*") 

    assert glob.globmatch("src/Database.js", "src/**/*", flags=glob.GLOBSTAR)
    assert glob.globmatch("src/dir/Database.js", "src/**/*", flags=glob.GLOBSTAR)  
