import ctypes

import windows.com
import windows.generated_def as gdef



class IExaDemo(gdef.COMInterface):
    IID = gdef.generate_IID(0x45786100, 0x1111, 0x2222, 0x33, 0x33, 0x44, 0x55, 0x00, 0x00, 0x00, 0x01, name="IExaDemo", strid="45786100-1111-2222-3333-445500000001")

IExaDemo._functions_ = {
        # QueryInterface -> riid:REFIID, ppvObject:**void
        "QueryInterface": ctypes.WINFUNCTYPE(gdef.HRESULT, gdef.REFIID, ctypes.POINTER(gdef.PVOID))(0, "QueryInterface"),
        # AddRef ->
        "AddRef": ctypes.WINFUNCTYPE(gdef.ULONG)(1, "AddRef"),
        # Release ->
        "Release": ctypes.WINFUNCTYPE(gdef.ULONG)(2, "Release"),
        # add -> x:UINT, y:UINT, res:*UINT
        "add": ctypes.WINFUNCTYPE(gdef.HRESULT, gdef.UINT, gdef.UINT, ctypes.POINTER(gdef.UINT))(3, "add"),
        # print_state ->
        "print": ctypes.WINFUNCTYPE(gdef.HRESULT, gdef.LPWSTR)(4, "dprint"),
    }

EXA_DEMO_SRV_CLSID = "45786100-4343-4343-4343-434343434343"

windows.com.init()

iunk = gdef.IUnknown()
print("CreateInstance {0}".format(EXA_DEMO_SRV_CLSID))
windows.com.create_instance(EXA_DEMO_SRV_CLSID, iunk, gdef.IUnknown.IID)
print("    OK: Got an IUnknown: {0}".format(iunk))

print("QueryInterface: IExaDemo.IID: {0}".format(IExaDemo.IID))
iexademo = iunk.query(IExaDemo)
print("    OK: {0}".format(iexademo))
print("Adding stuff:")
result = gdef.DWORD()
iexademo.add(0x41414141, 0x01010101, result)
print("    iexademo.add(0x41414141, 0x01010101) == {0:#x}".format(result.value))