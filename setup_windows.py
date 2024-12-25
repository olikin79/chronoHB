import os
from cx_Freeze import setup, Executable

versionDistribuee = "2.2.9"

os.environ["PYTHONIOENCODING"] = "utf-8"

# Dependencies are automatically detected, but they might need fine-tuning.
build_exe_options = {
    "includes": ["platform", "tkinter", "time", "datetime", "webbrowser", "subprocess", "sys", "os", "re", "copy", "socket",\
        "idlelib.tooltip", "pprint", "cgi", "requests", "hashlib", "CameraMotionDetection", "functools", "pywin32", "opencv-python", \
        "cryptography.fernet", "ftplib", "locale", "glob", "shutil", "random", "csv", "pathlib", "server", "threading", \
        "xlsxwriter", "math", "openpyxl", "urllib.request", "zipfile", "redmail", "cryptography.fernet", "paramiko"],
    "include_files": ["favicon.ico","create_shortcuts.py", "chronoHBGUI.py", "config.py", \
        "CameraMotionDetection.py", "FonctionsAssistance.py", "FonctionsDiffusionInternet.py", "FonctionsMetiers.py",  \
        "LICENSE", "openh264-1.8.0-win64.dll", "resultatsDiffusion.py", \
        "server.py", "Videos.html", \
        "cgi", "documentation", "gs", "gsview", "hooks", "IM", "maj", "media", "modeles", "secret", "www"]# , "texlive"
}

# build_mac_options = { "iconfile": "Icon.icns",
#                      "bundle_name": "Découpe Copies UM"}

directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

msi_data = {
    "Shortcut": [
                ("DesktopShortcut", "DesktopFolder", "ChronoHB", "TARGETDIR", "[TARGETDIR]ChronoHB.exe", None, "IconId", None, None, None, None, 'TARGETDIR'),
                ("StartMenuShortcut", "ProgramMenuFolder", "ChronoHB", "TARGETDIR", "[TARGETDIR]ChronoHB.exe", None, "IconId", None, None, None, None, 'TARGETDIR')
    ],
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None, "Chronométrage de courses", "IconId", None),
    ],
    "Icon": [
        ("IconId", "favicon.ico"),
    ],
}

build_msi_options = {"upgrade_code": "{66212526-7761-6E69-6F6E-6C129E797817}",
                     "target_name" :"ChronoHB",
                     "data": msi_data,
                     # Associer l'extension .chb au type ChronoHBFile
                    "extensions": [
                                # open chb files
                                {
                                "extension": "chb",
                                "verb": "open",
                                "executable": "chronoHB.exe",
                                "context": "Ouvre les fichiers chb",
                                # "argument": '"%1"',
                                },
                        ],
                    }

setup(
    name="ChronoHB",
    version=versionDistribuee,
    description="Chronométrage de courses",
    options={"build_exe": build_exe_options,
             "bdist_msi": build_msi_options},
    executables=[Executable("chronoHB.pyw", base="gui", target_name='chronoHB', copyright="Copyright (C) 2024 chronoHB",icon="favicon.ico")],
)