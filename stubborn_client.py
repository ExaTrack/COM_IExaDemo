import ctypes
import struct

import windows.rpc
import windows.generated_def as gdef
from windows.rpc import ndr

IID_IExaDemo = gdef.GUID.from_string("45786100-1111-2222-3333-445500000001")
CLSID_ExaDemoSrv = gdef.GUID.from_string("45786100-4343-4343-4343-434343434343")

windows.com.init()

comcatalog = gdef.IComCatalog()
windows.com.create_instance("00000346-0000-0000-c000-000000000046", comcatalog) # Retrieve the COM Catalog to get a IComClassInfo

comclassinfo = gdef.IComClassInfo()
comcatalog.GetClassInfo(CLSID_ExaDemoSrv, gdef.IComClassInfo.IID, comclassinfo)

propin = gdef.IActivationPropertiesIn()
windows.com.create_instance("00000338-0000-0000-c000-000000000046", propin) # Create a PropertyIN

# Simple Example : We directly ask for a pointer to a IID_IExaDemo
propin.AddRequestedIIDs(1, IID_IExaDemo)


propin_init = propin.query(gdef.IInitActivationPropertiesIn)
propin_as_priv = propin.query(gdef.IPrivActivationPropertiesIn)
propin_as_stage = propin.query(gdef.IActivationStageInfo)

propin_init.SetClassInfo(ctypes.cast(comclassinfo, gdef.IUnknown))
propin_init.SetClsctx(4)
propin_as_stage.SetStageAndIndex(gdef.CLIENT_CONTEXT_STAGE, 0) # We are a Client activator

propout = gdef.IActivationPropertiesOut()
remiunknown = gdef.IUnknown()
propin_as_priv.DelegateCreateInstance(remiunknown, propout)

# propout_as_prop = propout.query(gdef.IActivationProperties)
propout_as_priv = propout.query(gdef.IPrivActivationPropertiesOut)

propout_as_scmreply = propout.query(gdef.IScmReplyInfo)
rpiv_infoptr = gdef.PPRIV_RESOLVER_INFO()
propout_as_scmreply.GetResolverInfo(rpiv_infoptr)

resolver_info = rpiv_infoptr[0]
# xx = gdef.PRIV_RESOLVER_INFO2.from_address(ctypes.addressof(resolver_info))



psa = resolver_info.OxidInfo.psa[0]
ipidRemUnknown = resolver_info.OxidInfo.ipidRemUnknown

# priv_scm_info = gdef.PRIV_SCM_INFO()
# priv_scm_info.pwszWinstaDesktop = ctypes.cast(ctypes.c_wchar_p("ABCD"), ctypes.POINTER(gdef.WCHAR))
# prop_as_scm_req.SetScmInfo(priv_scm_info)

# Retrieve info about the IPID..
nb_interface = gdef.DWORD()
iids = gdef.LPGUID()
results = ctypes.POINTER(gdef.HRESULT)()
interfaces = ctypes.pointer(gdef.PMInterfacePointer())


propout_as_priv.GetMarshalledResults(nb_interface, iids, results, interfaces)



iunk_objref = interfaces[0][0].objref
# mcls_objref = interfaces[1][0].objref
# windows.utils.sprint(iunk_objref.std) # ALLER !!!

# assert objref.iid == gdef.IRemUnknown.IID
# assert iunk_objref.iid == gdef.IUnknown.IID
# assert mcls_objref.iid == gdef.GUID.from_string("11223344-5555-6666-7777-889900000002")



target_alpc_endpoint = psa.bidings[0]
assert target_alpc_endpoint.startswith("ncalrpc:[")
target_alpc_server = "\\RPC Control\\" + target_alpc_endpoint[len("ncalrpc:["):-1]
client = windows.rpc.RPCClient(target_alpc_server)

# TODO: IRemQueryInterface ?



# remunk = client.bind(gdef.IRemUnknown.IID, (0, 0))
#
# target_id = gdef.GUID.from_string("11223344-5555-6666-7777-889900000002")
# params = bytearray(iunk_objref.std.ipid)[:] + struct.pack("<I", 12) + struct.pack("<I", 2) + struct.pack("<I", 2) + bytearray(target_id) + bytearray(target_id)
# params = bytearray(iunk_objref.std.ipid)[:] + struct.pack("<I", 12) + struct.pack("<I", 1) + struct.pack("<I", 1) + bytearray(target_id)
# rem_queryi_response = client.call(remunk, 3, params, ipid=ipidRemUnknown) # Works !
# # client.call(remunk, 3, params, ipid=iunk_objref.std.ipid) # Crash the server :D Maybe we can play with the IPID ? :')
#
#
# # Parse reponse to RemoteQueryInterface
# stream = ndr.NdrStream(rem_queryi_response)
# orpcthat = gdef.ORPCTHAT32.from_buffer_copy(stream.read(ctypes.sizeof(gdef.ORPCTHAT32)))
# localthat = gdef.LOCALTHAT32.from_buffer_copy(stream.read(ctypes.sizeof(gdef.LOCALTHAT32)))
# hardcoded_ipid = gdef.GUID.from_buffer_copy(rem_queryi_response[72:88]) # real parsing is below
# sream = stream.read(8)
# assert sream == b"\x00\x00\x02\x00\x01\x00\x00\x00", repr(sream)
# reminterface = gdef.REMQIRESULT.from_buffer_copy(stream.data)
# assert hardcoded_ipid == reminterface.std.ipid

iid = client.bind(IID_IExaDemo, (0, 0))

# client.call(iid, 3, b"\x41\x41\x41\x41\x01\x01\x01\x01", ipid=iunk_objref.std.ipid)
# client.call(iid, 3, b"\x41\x41\x41\x41\x01\x01\x01\x01", ipid=mcls_objref.std.ipid)
# client.call(iid, 3, b"\x41\x41\x41\x41\x01\x01\x01\x01", ipid=hardcoded_ipid)
# addrep = client.call(iid, 3, b"\x41\x41\x41\x41\x01\x01\x01\x01", ipid=reminterface.std.ipid)
addrep = client.call(iid, 3, b"\x41\x41\x41\x41\x01\x01\x01\x01", ipid=iunk_objref.std.ipid)
addstream = ndr.NdrStream(addrep)
orpcthat = gdef.ORPCTHAT32.from_buffer_copy(bytearray(addstream.read(ctypes.sizeof(gdef.ORPCTHAT32))))
localthat = gdef.LOCALTHAT32.from_buffer_copy(bytearray(addstream.read(ctypes.sizeof(gdef.LOCALTHAT32))))
result = addstream.partial_unpack("<I")[0]
assert result == 0x41414141 + 0x01010101
print("Addition is OK !")