# IExaDemo COM Local Server

This repository contains the source code and Makefile necessary to compile the IExaDemo Local COM Server.
This COM server is the base playground for our blog article [BLOG LINK] about DCOM & ALPC.

It can also be of use for anyone looking to develop a working COM server in C and explore the inner working of LRPC/DCOM in a local computer. This project also aims to be a good example of a standalone Makefile for COM server & proxy compilation from the `.idl` and `.c` implementation files.
The code should compile in both 32 bits & 64 bits.

A simple python client is also provided in `client.py` as an example of use.

This code exposes the `IExaDemo` interface (`45786100-1111-2222-3333-445500000001`) and should be installed as a `EXA_DEMO_SRV_CLSID` (`45786100-4343-4343-4343-434343434343`).


## Compilation

This project is meant to be compiled (and was tested) with `VCForPython27.msi` (Microsoft Visual C++ Compiler for Python 2.7 9.0.0.30729). This package is a good way to install a fully working Windows compilation chain without any heavy IDE & visual studio package :)

`VCForPython27.msi` (sha256: 070474DB76A2E625513A5835DF4595DF9324D820F9CC97EAB2A596DCBC2F5CBF) can be found here : [TODO LINK]

Once installed, the x64 environment can be started from a `cmd.exe` with the command line:

```
    cmd.exe /k "%LOCALAPPDATA%\Programs\Common\Microsoft\Visual C++ for Python\9.0\vcvarsall.bat" x64
```

Example:

```
    cmd >cmd.exe /k "%LOCALAPPDATA%\Programs\Common\Microsoft\Visual C++ for Python\9.0\vcvarsall.bat" x64
    Setting environment for using Microsoft Visual Studio 2008 x64 tools.
    cmd >
```

The server and proxy DLL can then be compiled by launching `nmake` from the project directory in the previously open `cmd`.

Example:

```
    C:\Users\WDAGUtilityAccount\Desktop\PublicLocalServer>nmake

    Microsoft (R) Program Maintenance Utility Version 9.00.30729.01
    Copyright (C) Microsoft Corporation.  All rights reserved.

            midl /out .\dist\amd64 src\iexademo.idl
    [...]
    Generated .\dist\amd64\IExaDemo_server_64.exe
    Generated .\dist\amd64\IExaDemo_proxy_64.dll
```

The same thing can be done for a 32bits client & proxy dll with the following initial cmd.exe command line:

```
    cmd.exe /k "%LOCALAPPDATA%\Programs\Common\Microsoft\Visual C++ for Python\9.0\vcvarsall.bat" x86`
```

In this case : the resulting files will be:

- `.\dist\x86\IExaDemo_server_32.exe`
- `.\dist\x86\IExaDemo_proxy_32.dll`

The makefile also offer the following rules:

- `nmake server` to only compile the server
- `nmake proxy` to only compile the proxy DLL

## Installation

The default rule of the makefile (`all`) only build the binaries. Three other rules allow installing them from the makefile:

- `nmake install_server` to install the server via `reg add`
- `nmake install_proxy` to install the proxy DLL `regsrv32`
- `nmake install` to install both

The installation must be done in an administrator shell, as it will write to `HKEY_CLASS_ROOT`.

Question: If someone knows how to generate a proxy DLL with a `DllRegisterServer` method using HKEY_CURRENT_USER, I would be glad to have some feedback !

## Testing the python client

To test the python COM client, a version of Python should be installed (2.7 or 3.6+) as well as `PythonForWindows`.
This module can be installed using `py -m pip install PythonForWindows`.

The client can then be tested using:

`py client.py`

The code output should look like:

```
PublicLocalServer>py client.py
CreateInstance 45786100-4343-4343-4343-434343434343
    OK: Got an IUnknown: <IUnknown at 0x1bb11c1d948>
QueryInterface: IExaDemo.IID: 45786100-1111-2222-3333-445500000001
    OK: <IExaDemo at 0x1bb11c1dbc8>
Adding stuff:
    iexademo.add(0x41414141, 0x01010101) == 0x42424242
```

Another window (The `IExaDemo_server.exe` one) should pop-up and print a lot of stuff :)
If this doesn't work, check that your python bitness match the bitness of the proxy DLL you compiled and installed.

## The IExaDemo Interface

The interface presented by the COM server, directly inherit `IUnknown` and present two additional methods:

```
    HRESULT add(
        [in] unsigned int x,
        [in] unsigned int y,
        [out] unsigned int *res
    );

    HRESULT print(
        [in][string] wchar_t* msg);
```

Calling these methodes from any COM client should result in some debug priting in the server console.

Example entered at the end of `py -i client.py`:


```
    # Python
    >>> iexademo.add(0x12345678, 0x11111111, result)
    # IExaDemo_server.exe OUTPUT:
    CALL:IExaDemoImplem_add
    [IExaDemoImplem_add] 0x12345678 + 0x11111111 = 0x23456789

    # Python
    >>> iexademo.print("My string parameter !")
    67372036
    # IExaDemo_server.exe OUTPUT:
    CALL:IExaDemoImplem_print
    [IExaDemoImplem_print] Msg: <My string parameter !>
```

## References

- https://learn.microsoft.com/en-us/windows/win32/com/registering-com-servers
- https://learn.microsoft.com/en-us/previous-versions/windows/desktop/automat/hello-sample
- https://www.codeproject.com/Articles/8679/Building-a-LOCAL-COM-Server-and-Client-A-Step-by-S [TODO: verif link]
- https://www.codeproject.com/Articles/13601/COM-in-plain-C#CLASS
- https://github.com/hakril/PythonForWindows