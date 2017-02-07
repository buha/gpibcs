import re
import subprocess

def updateVersionInFile(file, regexp, version):
    with open(file, "r") as sources:
        lines = sources.readlines()
    with open(file, "w") as f:
        for line in lines:
            try:
                # replace the line with the result of regex substitution
                f.write(re.sub(regexp, version, line))
            except:
                # copy the original line in case of matching failure
                f.write(line)

def updateVersion():
    designFile = "design.py"
    buildinstallerFile = "buildinstaller.wxs"

    p = subprocess.Popen(['git', 'describe', '--tags'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()

    # git describe fails, we're most likely running on Windows from the installation directory
    if out == b'':
        # don't update the version
        return

    version = out.decode("utf-8").rstrip('\n')

    updateVersionInFile(designFile, r'(v\d+\.\d+\.\d+)(-\d+-g[a-gA-G0-9]{7})?', version)
    updateVersionInFile(buildinstallerFile, r'ProductVersion = \"(\d+\.\d+\.\d+)(-\d+-g[a-gA-G0-9]{7})?\"',
                                             'ProductVersion = \"{}\"'.format(version))
