#!/usr/bin/env python
from smartcard.scard import *
import smartcard.util
import binascii
import array
import sys


def get_atr(reader):
    readerstates = [(reader, SCARD_STATE_UNAWARE)]
    hresult, newstates = SCardGetStatusChange(hcontext, 0, readerstates)
    if hresult != SCARD_S_SUCCESS:
        raise error, 'Unable to connect: ' + SCardGetErrorMessage(hresult)
    return binascii.hexlify(array.array('B', newstates[0][2])).upper()

def conn(readername, reset):
    anyproto = SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1
    hresult, hcard, dwActiveProtocol = SCardConnect(hcontext, readername, SCARD_SHARE_SHARED, anyproto)
    if hresult != SCARD_S_SUCCESS:
        raise error, 'Unable to connect: ' + SCardGetErrorMessage(hresult)
    hresult = SCardDisconnect(hcard, reset)
    if hresult != SCARD_S_SUCCESS:
        raise error, 'Unable to disconnect: ' + SCardGetErrorMessage(hresult)


try:
    atr = set()
    hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
    if hresult != SCARD_S_SUCCESS:
        raise error, 'Failed to establish context: ' + SCardGetErrorMessage(hresult)

    try:
        hresult, readers = SCardListReaders(hcontext, [])
        if hresult != SCARD_S_SUCCESS:
            raise error, 'Failed to list readers: ' + SCardGetErrorMessage(hresult)

        # locate the reader with a card            
        states = [(x, SCARD_STATE_UNAWARE) for x in readers]
        hresult, newstates = SCardGetStatusChange(hcontext, 0, states)
        foundcards = [x[0] for x in newstates if x[1] & SCARD_STATE_PRESENT]

        if len(foundcards) > 1:
            print >> sys.stderr, "Please insert just a single card that shall be tested"
            sys.exit(1)
        reader = foundcards[0]

        # Get the cold ATR
        conn(reader, SCARD_UNPOWER_CARD)
        atr.add(get_atr(reader))
        # Make two soft-resets
        conn(reader, SCARD_RESET_CARD)
        atr.add(get_atr(reader))
        conn(reader, SCARD_RESET_CARD)
        atr.add(get_atr(reader))
    finally:
        hresult = SCardReleaseContext(hcontext)
        if hresult != SCARD_S_SUCCESS:
            raise error, 'Failed to release context: ' + SCardGetErrorMessage(hresult)
    # print results
    for a in atr:
        print a
    sys.exit(0 if len(atr) == 1 else 1)

except error, e:
    print e
    sys.exit(1)
