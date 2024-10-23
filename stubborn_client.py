import ctypes
import struct

import windows.rpc
import windows.generated_def as gdef
from windows.rpc import ndr

IID_IExaDemo = gdef.GUID.from_string("45786100-1111-2222-3333-445500000001")
CLSID_ExaDemoSrv = gdef.GUID.from_string("45786100-4343-4343-4343-434343434343")

windows.com.init()

# Retrieve the COM Catalog to get a IComClassInfo
comcatalog = gdef.IComCatalog()
windows.com.create_instance("00000346-0000-0000-c000-000000000046", comcatalog)

# Retrieve the IComClassInfo on CLSID_ExaDemoSrv
comclassinfo = gdef.IComClassInfo()
comcatalog.GetClassInfo(CLSID_ExaDemoSrv, gdef.IComClassInfo.IID, comclassinfo)

# Create an ActivationPropertiesIn
propin = gdef.IActivationPropertiesIn()
windows.com.create_instance("00000338-0000-0000-c000-000000000046", propin)

# Query the interfaces we need to fill the ActivationPropertiesIn
propin_init = propin.query(gdef.IInitActivationPropertiesIn)
propin_as_priv = propin.query(gdef.IPrivActivationPropertiesIn)
propin_as_stage = propin.query(gdef.IActivationStageInfo)

# Fill the ActivationPropertiesIn
# Simple example : We directly ask for a pointer to an IID_IExaDemo
# We could ask for a IUnknown and then use RemQueryInterface
propin.AddRequestedIIDs(1, IID_IExaDemo)
propin_init.SetClassInfo(ctypes.cast(comclassinfo, gdef.IUnknown))
propin_init.SetClsctx(gdef.CLSCTX_LOCAL_SERVER)
propin_as_stage.SetStageAndIndex(gdef.CLIENT_CONTEXT_STAGE, 0) # We are a Client activator

# Make the actual CreateInstance
propout = gdef.IActivationPropertiesOut()
remiunknown = gdef.IUnknown()
propin_as_priv.DelegateCreateInstance(remiunknown, propout)

# Query the interfaces we need to from the ActivationPropertiesOut
propout_as_priv = propout.query(gdef.IPrivActivationPropertiesOut)
propout_as_scmreply = propout.query(gdef.IScmReplyInfo)

rpiv_infoptr = gdef.PPRIV_RESOLVER_INFO() # Structure may change on older windows and be PPRIV_RESOLVER_INFO_LEGACY
propout_as_scmreply.GetResolverInfo(rpiv_infoptr)

resolver_info = rpiv_infoptr[0]
psa = resolver_info.OxidInfo.psa[0] # Retrieve the bidings to our COM server
# ipidRemUnknown = resolver_info.OxidInfo.ipidRemUnknown # Useful for IRemQueryInterface

# Retrieve info about the IPID from GetMarshalledResults
nb_interface = gdef.DWORD()
iids = gdef.LPGUID()
results = ctypes.POINTER(gdef.HRESULT)()
interfaces = ctypes.pointer(gdef.PMInterfacePointer())
propout_as_priv.GetMarshalledResults(nb_interface, iids, results, interfaces)

iexademo_objref = interfaces[0][0].objref

# Parse the RPC biding and connect to the related ALPC Port
target_alpc_endpoint = psa.bidings[0]
assert target_alpc_endpoint.startswith("ncalrpc:[")
target_alpc_server = "\\RPC Control\\" + target_alpc_endpoint[len("ncalrpc:["):-1]
client = windows.rpc.RPCClient(target_alpc_server)

# RPC: Bind to the IID on ou server
iid = client.bind(IID_IExaDemo, (0, 0))

# Parameters for IExaDemo.add(0x41414141 + 0x01010101)
addrep = client.call(iid, 3, b"\x41\x41\x41\x41\x01\x01\x01\x01", ipid=iexademo_objref.std.ipid)
# Raw parsing of the ORPCTHAT32 & LOCALTHAT32 & result
addstream = ndr.NdrStream(addrep)
orpcthat = gdef.ORPCTHAT32.from_buffer_copy(bytearray(addstream.read(ctypes.sizeof(gdef.ORPCTHAT32))))
localthat = gdef.LOCALTHAT32.from_buffer_copy(bytearray(addstream.read(ctypes.sizeof(gdef.LOCALTHAT32))))
result = addstream.partial_unpack("<I")[0]
assert result == 0x41414141 + 0x01010101
print("Addition is OK : {0:#x} !".format(result))

# Verify that the proxy DLL was never loaded in the process
assert not [m for m in windows.current_process.peb.modules if "proxy" in m.name], "Proxy DLL was loaded :("
print("Proxy DLL was never loaded !")