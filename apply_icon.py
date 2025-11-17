import os
import subprocess, argparse
from PIL import Image
import win32gui
import win32ui
import win32con
import win32api
import numpy

import ctypes
from ctypes import POINTER, Structure, c_wchar, c_int, sizeof, byref
from ctypes.wintypes import BYTE, WORD, DWORD, LPWSTR, LPSTR

import icoextract

VALID_IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".gif"]


HICON = c_int
LPTSTR = LPWSTR
TCHAR = c_wchar
MAX_PATH = 260
FCSM_ICON_FILE = 0x00000010
FCS_FORCE_WRITE = 0x00000002
SHGFI_ICON_LOCATION = 0x000001000

ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)


class GUID(Structure):
    """
    Structure definition.
    See https://docs.python.org/3/library/ctypes.html#structures-and-unions
    """

    _fields_ = [("Data1", DWORD), ("Data2", WORD), ("Data3", WORD), ("Data4", BYTE * 8)]

class SHFolderCustomSettings(Structure):
    """
    Structure definition.
    """

    _fields_ = [
        ("dw_size", DWORD),
        ("dw_mask", DWORD),
        ("pvid", POINTER(GUID)),
        ("pszWebViewTemplate", LPTSTR),
        ("cchWebViewTemplate", DWORD),
        ("pszWebViewTemplateVersion", LPTSTR),
        ("pszInfoTip", LPTSTR),
        ("cchInfoTip", DWORD),
        ("pclsid", POINTER(GUID)),
        ("dwFlags", DWORD),
        ("psz_icon_file", LPTSTR),
        ("cch_icon_file", DWORD),
        ("i_icon_index", c_int),
        ("pszLogo", LPTSTR),
        ("cchLogo", DWORD),
    ]


def extract_exe_icon(exe_path, ico_path):
    try:
        extractor = icoextract.IconExtractor(exe_path)

        # OLD API: returns BytesIO object or None
        icon_stream = extractor.get_icon()
        if icon_stream is None:
            print("No icon found in:", exe_path)
            return None

        # MUST convert BytesIO → raw bytes
        icon_bytes = icon_stream.getvalue()

        with open(ico_path, "wb") as f:
            f.write(icon_bytes)

        print("✓ Extracted icon:", ico_path)
        return ico_path

    except Exception as e:
        print("EXE icon extraction failed:", e)
        return None

# def extract_icon_from_exe(exe_path, ico_path):
#     large = extract_best_icon(exe_path)
#     # large, small = win32gui.ExtractIconEx(exe_path, 0)

#     print(f"LARGE: {large}")
    
#     dc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
#     cdc = dc.CreateCompatibleDC()

#     bitmap = win32ui.CreateBitmap()
#     bitmap.CreateCompatibleBitmap(dc, ico_x, ico_y)

#     cdc.SelectObject(bitmap)
#     cdc.DrawIcon((0, 0), large)

#     output = numpy.frombuffer(bitmap.GetBitmapBits(True), dtype = numpy.uint8).reshape((ico_x, ico_y, 4))

#     dc.DeleteDC()
#     cdc.DeleteDC()

#     win32gui.DeleteObject(bitmap.GetHandle())

#     # 2. Convert BGRA → RGBA for PIL
#     rgba = output[..., [2, 1, 0, 3]]   # Swap channels

#     img = Image.fromarray(rgba, "RGBA")

#     # 3. Convert NumPy array → PIL Image
#     new_w = ico_x * 6
#     new_h = ico_y * 6
#     img = img.resize((new_w, new_h), resample=Image.NEAREST)

#     # 5. Save as .ico
#     img.save(ico_path, format="ICO")
#     return 

def find_exe_or_icon(folder_path, args):
    path_to_exe_or_icon = None
    exe_path = None
    image_path = None
    print("TEST")

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in filenames:
            base, extension = os.path.splitext(file)

            if extension == ".ico" and args.ico:
                print("has ico")
                return os.path.join(dirpath, file)

            if extension == ".exe" and exe_path is None and args.exe:
                substrings = [string.lower() for string in args.restricted_keywords]
                if not any(sub in base.lower() for sub in substrings):
                    print("has exe")
                    exe_path = os.path.join(dirpath, file)

            if extension == VALID_IMAGE_EXTS and args.image:
                print("has img")
                image_path = os.path.join(dirpath, file)

    icon_path = os.path.join(folder_path,"icon.ico")

    if exe_path is not None:
        extract_exe_icon(exe_path, icon_path)
        return icon_path
    
    elif image_path is not None:
        print("image")
        img = Image.open(image_path)
        img.save(icon_path)

    return icon_path

def set_icon(folder_path, icon_path, icon_index=0):
    """
    Applies 'icon_path' to 'folder_path'
    :param folder_path:
    :param icon_path:
    :param icon_index:
    :return:
    """

    shell32 = ctypes.windll.shell32

    folder_path = str(os.path.abspath(folder_path))
    icon_path = str(os.path.abspath(icon_path))

    fcs = SHFolderCustomSettings()
    fcs.dw_size = sizeof(fcs)
    fcs.dw_mask = FCSM_ICON_FILE
    fcs.psz_icon_file = icon_path
    fcs.cch_icon_file = 0
    fcs.i_icon_index = icon_index

    gs_fcs = shell32.SHGetSetFolderCustomSettings(byref(fcs), folder_path, FCS_FORCE_WRITE)
    if gs_fcs:
        raise WindowsError(win32api.FormatMessage(gs_fcs))

    sfi = SHFileInfo()
    gs_fcs = shell32.SHGetFileInfoW(folder_path, 0, byref(sfi), sizeof(sfi), SHGFI_ICON_LOCATION)
    if gs_fcs == 0:
        raise WindowsError(win32api.FormatMessage(gs_fcs))

    # index = shell32.Shell_GetCachedImageIndexW(sfi.szDisplayName, sfi.iIcon, 0)
    # if index == -1:
    #     raise WindowsError()

    shell32.SHUpdateImageW(sfi.szDisplayName, sfi.iIcon, 0, 0)

class SHFileInfo(Structure):
    """
    Structure definition.
    """

    _fields_ = [
        ("hIcon", HICON),
        ("iIcon", c_int),
        ("dwAttributes", DWORD),
        ("szDisplayName", TCHAR * MAX_PATH),
        ("szTypeName", TCHAR * 80),
    ]

def apply_subfolder(parent_path, args, depth=0):
    if depth == 0:
        for subfolder in os.listdir(parent_path):
            subfolder_path = (os.path.join(parent_path, subfolder))
            if os.path.isdir(subfolder_path):
                print(subfolder_path)
                icon_path = find_exe_or_icon(subfolder_path, args)
                set_icon(subfolder_path, icon_path)
    else:
        for subfolder in os.listdir(parent_path):
            subfolder_path = (os.path.join(parent_path, subfolder))
            if os.path.isdir(subfolder_path):
                apply_subfolder(subfolder_path, args, depth-1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str, required=True)
    parser.add_argument("--is-parent", action="store_true")
    parser.add_argument("--depth", type=int, default=0)
    parser.add_argument("--restricted-keywords", type=str, nargs="*", default="unist")

    parser.add_argument("--exe", type=bool, default=True)
    parser.add_argument("--ico", type=bool, default=False)
    parser.add_argument("--image", type=bool, default=False)

    
    args = parser.parse_args()

    assert args.directory, "Invalid directory"

    if args.is_parent is None:
        icon_path = find_exe_or_icon(args.directory, args)
        set_icon(args.directory, icon_path)
    else:
        apply_subfolder(args.directory, args, args.depth)

if __name__ == "__main__":
    main()