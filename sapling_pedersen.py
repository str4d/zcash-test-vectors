#!/usr/bin/env python3
from sapling_generators import find_group_hash, NOTE_POSITION_BASE, WINDOWED_PEDERSEN_RANDOMNESS_BASE
from sapling_jubjub import ENDIANNESS, Fr


#
# Pedersen hashes
#

def I_D_i(D, i):
    return find_group_hash(D, (i - 1).to_bytes(4, byteorder=ENDIANNESS))

def encode_chunk(mj):
    (s0, s1, s2) = mj
    return (1 - 2*s2) * (1 + s0 + 2*s1)

def encode_segment(Mi):
    ki = len(Mi) / 3
    Michunks = [Mi[i:i+3] for i in range(0, len(Mi), 3)]
    assert(len(Michunks) == ki)
    return Fr(sum([encode_chunk(Michunks[j-1]) * 2**(4*(j-1)) for j in range(1, ki + 1)]))

def cldiv(n, divisor):
    return (n + (divisor - 1)) // divisor

c = 63

def pedersen_hash_to_point(D, M):
    # Pad M to a multiple of 3 bits
    Mdash = M + [0] * ((-len(M)) % 3)
    n = cldiv(len(Mdash), 3 * c)
    Msegs = [Mdash[i:i+(3*c)] for i in range(0, len(Mdash), 3*c)]
    assert(len(Msegs) == n)
    return sum([I_D_i(D, i) * encode_segment(Msegs[i-1]) for i in range(1, n + 1)])

def pedersen_hash(D, M):
    return pedersen_hash_to_point(D, M).u.bits(255)

def mixing_pedersen_hash(P, x):
    return P + NOTE_POSITION_BASE * x


#
# Pedersen commitments
#

def windowed_pedersen_commitment(r, s):
    return pedersen_hash_to_point(b'Zcash_PH', s) + WINDOWED_PEDERSEN_RANDOMNESS_BASE * r

def homomorphic_pedersen_commitment(rcv, D, v):
    return find_group_hash(D, b'v') * v + find_group_hash(D, b'r') * rcv
