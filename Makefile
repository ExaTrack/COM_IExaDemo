!IF "$(PROCESSOR_ARCHITECTURE)" == "x86"
# 32 bits target
TARGETDIR=.\dist\x86
SUFFIX=_32
! ELSE IF "$(PROCESSOR_ARCHITECTURE)" == "AMD64"
# 64bits target
TARGETDIR=.\dist\amd64
SUFFIX=_64
!ELSE
!ERROR Unknown PROCESSOR_ARCHITECTURE: $(PROCESSOR_ARCHITECTURE)
!ENDIF

# Useful sources
#   https://learn.microsoft.com/en-us/windows/win32/com/building-and-registering-a-proxy-dll


# Source definitions
MIDL_SRC=iexademo.idl
SERVER_IMPLEM_SRC=iexademo_implem.c
PROXY_DEF=iexademo_proxy.def

## File generated by midl
MIDL_OUT_H=$(TARGETDIR)\iexademo.h
MIDL_OUT_I=$(TARGETDIR)\iexademo_i.c
MIDL_OUT_P=$(TARGETDIR)\iexademo_p.c
MIDL_OUT_DLLDATA_C=$(TARGETDIR)\dlldata.c

MIDL_OUTPUT=$(MIDL_OUT_H) $(MIDL_OUT_I) $(MIDL_OUT_P) $(MIDL_OUT_DLLDATA_C)

PROXYSTUBOBJS = $(TARGETDIR)\dlldata.obj $(TARGETDIR)\iexademo_p.obj $(TARGETDIR)\iexademo_i.obj
PROXYSTUBLIBS = kernel32.lib rpcns4.lib rpcrt4.lib uuid.lib

# Target definitions
SERVER_EXE=$(TARGETDIR)\IExaDemo_server$(SUFFIX).exe
PROXY_DLL=$(TARGETDIR)\IExaDemo_proxy$(SUFFIX).dll

#Variables for proxy generated

# Add all output of midl ?

all: $(SERVER_EXE) $(PROXY_DLL)
    @echo Generated $(SERVER_EXE)
    @echo Generated $(PROXY_DLL)

server:
    @echo Generated $(SERVER_EXE)

proxy: $(PROXY_DLL)
    @echo Generated $(PROXY_DLL)

clean:
    rmdir /S /Q dist


$(SERVER_EXE): $(SERVER_IMPLEM_SRC) $(MIDL_OUT_H) $(MIDL_OUT_I)
    cl /I$(TARGETDIR) /DEBUG:FULL /Z7 $(SERVER_IMPLEM_SRC) $(MIDL_OUT_I) /Fo"$(TARGETDIR)\\" /link /OUT:$(SERVER_EXE)

# proxy rules

$(TARGETDIR)\iexademo_p.obj $(TARGETDIR)\dlldata.obj: $(MIDL_OUT_P) $(MIDL_OUT_DLLDATA_C)
    CL /c /DWIN32 /DREGISTER_PROXY_DLL /Fo"$(TARGETDIR)\\" $(MIDL_OUT_P) $(MIDL_OUT_DLLDATA_C)

$(TARGETDIR)\iexademo_i.obj : $(MIDL_OUT_I)
    CL /c /DWIN32 /Fo"$(TARGETDIR)\\" $(MIDL_OUT_I)

$(PROXY_DLL) : $(PROXYSTUBOBJS) $(PROXY_DEF)
    link /dll /out:$(PROXY_DLL) /def:$(PROXY_DEF) $(PROXYSTUBOBJS) $(PROXYSTUBLIBS)


# Common rules
$(MIDL_OUTPUT): $(MIDL_SRC) $(TARGETDIR)
    midl /out $(TARGETDIR) $**
# Create target directory
$(TARGETDIR):
    mkdir $(TARGETDIR)