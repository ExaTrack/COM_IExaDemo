#include <windows.h>
// #include <Objidlbase.h>
// #include <combaseapi.h>
#include "iexademo.h"

#pragma comment(lib, "Ole32")
#pragma comment(lib, "Oleaut32")
#define DLLEXPORT __declspec( dllexport )

// https://www.codeproject.com/Articles/13601/COM-in-plain-C#CLASS
// https://learn.microsoft.com/en-us/previous-versions/windows/desktop/automat/hello-sample

BOOL DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved) {
   switch (reason) {
    case DLL_PROCESS_ATTACH:
        printf("[" __FUNCTION__ "] Process attach !\n");
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
      break;
  }
  printf("[" __FUNCTION__ "] Bye !\n");
  return TRUE;
}

/* mon implem de class */

typedef struct {
    IExaDemoVtbl* lpVtbl;
    DWORD count;
    DWORD last_res;
    DWORD secret;
} IExaDemoImplem;


STDAPI IExaDemoImplem_QueryInterface(IExaDemoImplem *this, REFIID riid, void** ppv) {
    LPOLESTR x = NULL;
    IMarshal* marsh = NULL;

    printf("CALL:" __FUNCTION__ "\n");
    StringFromCLSID(riid, &x);
    printf("[" __FUNCTION__ "]  * riid: %ws !\n", x);


    if (IsEqualIID(riid, &IID_IUnknown)) {
        printf("[" __FUNCTION__ "]  * Asking for IID_IUnknown: I CAN DO THAT !\n");
        *ppv = this;
        this->lpVtbl->AddRef(this);
        return S_OK;
    }

    if (IsEqualIID(riid, &IID_IExaDemo)) {
        printf("[" __FUNCTION__ "]  * Asking for IID_IExaDemo: I CAN DO THAT !\n");
        *ppv = this;
        this->lpVtbl->AddRef(this);
        return S_OK;
    }

    // if (IsEqualIID(riid, &IID_IMarshal)) {
        // printf("  * Asking for IID_IMarshal: Lol!\n");
        // CoGetStandardMarshal(&IID_IExaDemo, this, MSHCTX_LOCAL, NULL, MSHLFLAGS_NORMAL, &marsh);
        // *ppv = marsh;
        // marsh->lpVtbl->AddRef();
        // return S_OK;
    // }

    // if (IsEqualIID(riid, &IID_INoMarshal)) {
        // printf("  * Asking for IID_INOMarshal: Lol!\n");
        // *ppv = this;
        // return S_OK
    // }

    printf("[" __FUNCTION__ "]  * E_NOINTERFACE\n");
    *ppv = NULL;
    return E_NOINTERFACE;
}

STDAPI IExaDemoImplem_AddRef(IExaDemoImplem *this) {
    printf("CALL:" __FUNCTION__ "\n");
    ++this->count;
    printf("[" __FUNCTION__ "] * new count = %d\n", this->count);
    return this->count;
}

STDAPI IExaDemoImplem_Release(IExaDemoImplem *this) {
    printf("CALL:" __FUNCTION__ "\n");
    --this->count;
    printf("[" __FUNCTION__ "] * new count = %d\n", this->count);
    return this->count;
}

STDAPI IExaDemoImplem_add(IExaDemoImplem *this, unsigned int x, unsigned int y, unsigned int *res) {
    printf("CALL:" __FUNCTION__ "\n");
    *res = (x + y);
    this->last_res = *res;
    printf("[" __FUNCTION__ "] 0x%x + 0x%x = 0x%x\n", x, y, *res);
    return S_OK;
}

STDAPI IExaDemoImplem_print(IExaDemoImplem *this, wchar_t* msg) {
        printf("CALL:" __FUNCTION__ "\n");
        printf("[" __FUNCTION__ "] POUET POUET\n");
        if (msg == NULL) {
            printf("[" __FUNCTION__ "] Msg: NULL\n");
        } else {
            printf("[" __FUNCTION__ "] Msg: <%ws>\n", msg);
        }
        return 0x04040404;
}

static IExaDemoVtbl IExaDemoImplem_Vtbl = {
    IExaDemoImplem_QueryInterface,
    IExaDemoImplem_AddRef,
    IExaDemoImplem_Release,
    IExaDemoImplem_add,
    IExaDemoImplem_print,
};

// Factory

STDAPI MyFactory_QueryInterface(IClassFactory *this, REFIID riid, void** ppv) {
    LPOLESTR x = NULL;

    printf("CALL:" __FUNCTION__ "\n");
    StringFromCLSID(riid, &x);
    printf("[" __FUNCTION__ "]  * riid: %ws !\n", x);

    if (IsEqualIID(riid, &IID_IClassFactory)) {
        printf("[" __FUNCTION__ "]  * Asking for IID_IClassFactory: I CAN DO THAT !\n");
        *ppv = this;
        return S_OK;
    }

    if (IsEqualIID(riid, &IID_IUnknown)) {
        printf("[" __FUNCTION__ "]  * Asking for IID_IUnknown: I CAN DO THAT !\n");
        *ppv = this;
        this->lpVtbl->AddRef(this);
        return S_OK;
    }

    printf("[" __FUNCTION__ "]  * E_NOINTERFACE\n");
    return E_NOINTERFACE;
}

STDAPI MyFactory_AddRef(IClassFactory *this) {
    printf("CALL:" __FUNCTION__ "\n");
    return S_OK;
}

STDAPI MyFactory_Release(IClassFactory *this) {
    printf("CALL:" __FUNCTION__ "\n");
    return 0;
}

STDAPI MyFactory_CreateInstance(IClassFactory *this, IUnknown *punkOuter, REFIID factoryGuid, void** ppv) {
    LPOLESTR x = NULL;
    IExaDemoImplem *thisout = NULL;

    printf("CALL:" __FUNCTION__ "\n");
    StringFromCLSID(factoryGuid, &x);
    printf("[" __FUNCTION__ "]   * factoryGuid: %ws !\n", x);

    if (punkOuter) {
        return CLASS_E_NOAGGREGATION;
    }

    if (IsEqualIID(factoryGuid, &IID_IExaDemo) || IsEqualIID(factoryGuid, &IID_IUnknown)) {
        printf("[" __FUNCTION__ "] CA MATCH !\n");

        thisout = GlobalAlloc(GMEM_FIXED, sizeof(IExaDemoImplem)); // malloc ?
        thisout->lpVtbl = &IExaDemoImplem_Vtbl;
        thisout->last_res = 0;
        thisout->count = 1;
        thisout->secret = 42;

        *ppv =  thisout;
        printf("[" __FUNCTION__ "] Instance created !!!\n");
        return S_OK;
    }

    *ppv = NULL;
    return E_NOINTERFACE;
}

STDAPI MyFactory_LockServer(IClassFactory *this, BOOL lock) {
    printf(__FUNCTION__ "\n");
    printf("[" __FUNCTION__ "] LOCK LOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCKLOCK\n");
    return S_OK;
}

static IClassFactoryVtbl MyFactoryVtble = {
    MyFactory_QueryInterface,
    MyFactory_AddRef,
    MyFactory_Release,
    MyFactory_CreateInstance,
    MyFactory_LockServer,
};

static IClassFactory MyFactory = {&MyFactoryVtble};

/*END FACTORY */

HANDLE g_hEvent;

#define MIDL_DEFINE_GUID(type,name,l,w1,w2,b1,b2,b3,b4,b5,b6,b7,b8) \
        const type name = {l,w1,w2,{b1,b2,b3,b4,b5,b6,b7,b8}}

MIDL_DEFINE_GUID(IID, TestIID,0x43434343,0x4343,0x4343,0x43,0x43,0x43,0x43,0x43,0x43,0x43,0x43);

#undef MIDL_DEFINE_GUID

int main(int argc, char *argv[]) {
    CLSID factoryClsId;
    DWORD dwRegister = 0;
    LPOLESTR x = NULL;
    DWORD tst = 0;
    ITypeLib* pTypeLib;
    HRESULT hr;

	// hr = LoadTypeLibEx(L"mycls.tlb", REGKIND_NONE , &pTypeLib);
    // printf("hr = %x\n", hr);
	// pTypeLib->lpVtbl->Release(pTypeLib);


    printf("CALL:" __FUNCTION__ "\n");

    printf("[" __FUNCTION__ "] Hello World !\n");
    SleepEx(1000, 0);

    // if (CLSIDFromString(L"43434343-4343-4343-4343-434343434343", &factoryClsId) != NOERROR) {
        // printf("CLSIDFromString error !\n");
        // SleepEx(1000, 0);
        // return 1;
    // }

    StringFromCLSID(&TestIID, &x);
    printf("[" __FUNCTION__ "] * factoryClsId: %ws !\n", x);

    // Initialize COM
    // CoInitializeEx(NULL, COINIT_MULTITHREADED);
    CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);

    g_hEvent = CreateEvent(NULL, FALSE, FALSE, NULL);

    // Register our const factory !
    // CoRegisterClassObject(factoryClsId, MyFactory, CLSCTX_LOCAL_SERVER, REGCLS_SUSPENDED|REGCLS_MULTIPLEUSE, &dwRegister);
    CoRegisterClassObject(&TestIID, &MyFactory, CLSCTX_LOCAL_SERVER, REGCLS_MULTIPLEUSE, &dwRegister);
    printf("[" __FUNCTION__ "] Register: %d\n", dwRegister);

    printf("[" __FUNCTION__ "] Going to wait !\n");
    // WaitForSingleObject(g_hEvent, INFINITE);

    /* Wait & dispatch call in COINIT_APARTMENTTHREADED */
    CoWaitForMultipleHandles(8, 0x100000, 1, &g_hEvent, &tst);
    // CoRevokeClassObject(dwRegister);
    // CoUninitialize();
}