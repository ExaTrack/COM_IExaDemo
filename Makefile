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
## exademo.h generated by midl
MIDL_OUT_H=$(TARGETDIR)\iexademo.h
MIDL_OUT_I=$(TARGETDIR)\iexademo_i.c
SERVER_IMPLEM_SRC=iexademo_implem.c

# Target definitions
SERVER_EXE=$(TARGETDIR)\IExaDemo_server$(SUFFIX).exe
PROXY_DLL=$(TARGETDIR)\IExaDemo_proxy$(SUFFIX).dll

# Add all output of midl ?
MIDL_OUTPUT=$(TARGETDIR)\dlldata.c $(MIDL_OUT_H)

all: $(SERVER_EXE)
    @echo all done !


# SERVER_EXE rules
$(SERVER_EXE): $(SERVER_IMPLEM_SRC) $(MIDL_OUT_H) $(MIDL_OUT_I)
    cl /I$(TARGETDIR) /DEBUG:FULL /Fd$(TARGETDIR)implem.pdb /Z7 $(SERVER_IMPLEM_SRC) $(MIDL_OUT_I)

# proxy rules

# Common rules
$(MIDL_OUTPUT): $(MIDL_SRC) $(TARGETDIR)
    midl $** /out $(TARGETDIR)

# Create target directory
$(TARGETDIR):
    mkdir $(TARGETDIR)