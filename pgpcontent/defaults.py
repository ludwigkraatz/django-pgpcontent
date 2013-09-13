from contextlib import contextmanager

__all__ = ['get_defaults']

_key ="""-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG/MacGPG2 v2.0.18 (Darwin)

mI0EUHKLzQEEANvVUQh+2iv1hW4p4yKB3nMDWvpXLt427bZfSr2BmXVTTubGNyVi
CdvKfz5eA45a4ZmhxvIRsXz5/WXZijlp8KtLy4Q1CatAkcxVrb9Qp3G2C2Yz8KTE
QBjApLdaLlcZqOE3WiUVQ9+jCxGx3wjxl0qoM8wpcW9qowRGuSlG7CXbABEBAAG0
PkF1dG9nZW5lcmF0ZWQgS2V5IChHZW5lcmF0ZWQgYnkgZ251cGcucHkpIDxzaG93
cm9vbUBleHAtbi5vcmc+iLkEEwECACMFAlByi80CGy8HCwkIBwMCAQYVCAIJCgsE
FgIDAQIeAQIXgAAKCRBK1ByrVuHsScANA/9tbZUHO9XoGLMW6Dtwi2yVgiUrL2AK
Kvs44WHaYgs97D9PdKeQdbmPkWbnjmx3xsOj5oq6zmw3GgFetQbrjXYbE9UOSjvy
zFt3Av3eYA1OsPYcIKEQU8Fpg/CZl8v8n95zwHwX5pxtW6U7OMJlUsbT6/mUKrAm
xSqPyjvIalyplw==
=15+E
-----END PGP PUBLIC KEY BLOCK-----
-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG/MacGPG2 v2.0.18 (Darwin)

lQHYBFByi80BBADb1VEIftor9YVuKeMigd5zA1r6Vy7eNu22X0q9gZl1U07mxjcl
Ygnbyn8+XgOOWuGZocbyEbF8+f1l2Yo5afCrS8uENQmrQJHMVa2/UKdxtgtmM/Ck
xEAYwKS3Wi5XGajhN1olFUPfowsRsd8I8ZdKqDPMKXFvaqMERrkpRuwl2wARAQAB
AAP+PLCmn27N8qbkwGYmA8fQzvXVLxnUoZqOg/PI4YqfACoQtVtxrAtl51z/RguU
db+XWt+z2e6SjotBrtWg+HrL6ytaboYjvmir8mNdkosRqkP0OfGLhAf9J799QAZ8
hYPUqm67SacJVkmT0EEs9Bh3IFTiInt4tOPCuXCdZwWhW0ECAN+32HVc3V3LRnLs
ql/s3fNxFHoH2ywgI3IIverS/JV2KxrZGdBih3SloTUVrJzpizjVVmc8iCv71ZPd
iZpbEqECAPuN9qVldOVqlMfFvPdZAAjcQW3+KJzR2DxUIcrAnmm8lz8aRgaYkipg
YFuMHpP+LJwH+bRomVyDXj/BzoV3ovsCAPOgrMi7suZDSXmeBLB2McjvUen73I4R
nSmaVaKLdnDwaVWMly7Cojke4D7elOaEGikRnVnEza/TfumY7WL1Iq6rn7Q+QXV0
b2dlbmVyYXRlZCBLZXkgKEdlbmVyYXRlZCBieSBnbnVwZy5weSkgPHNob3dyb29t
QGV4cC1uLm9yZz6IuQQTAQIAIwUCUHKLzQIbLwcLCQgHAwIBBhUIAgkKCwQWAgMB
Ah4BAheAAAoJEErUHKtW4exJwA0D/21tlQc71egYsxboO3CLbJWCJSsvYAoq+zjh
YdpiCz3sP090p5B1uY+RZueObHfGw6PmirrObDcaAV61BuuNdhsT1Q5KO/LMW3cC
/d5gDU6w9hwgoRBTwWmD8JmXy/yf3nPAfBfmnG1bpTs4wmVSxtPr+ZQqsCbFKo/K
O8hqXKmX
=P5zj
-----END PGP PRIVATE KEY BLOCK-----"""


@contextmanager
def get_default_keys():
    global _key
    from django.conf import settings
    
    if not settings.DEBUG:
        raise Exception, 'please use your own keys in production!'
    # TODO: print warning!! just use for development
    
    yield _key
    #
    #if not settings.DEBUG:
    #    _key = ''