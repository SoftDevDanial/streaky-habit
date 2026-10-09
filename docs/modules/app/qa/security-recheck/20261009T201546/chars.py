"""Characters built from code points, so that no file in this folder holds a raw bidirectional control or an escape that a
tool could turn into one (the writing tool turns `backslash u XXXX` text into the raw character, which is how the first
version of probe_10 got a raw U+2029 inside a regular expression and failed to load)."""

BS = chr(92)

RLO, LRO, RLE, LRE, RLI, LRI, FSI, PDI = (chr(c) for c in (0x202E, 0x202D, 0x202B, 0x202A, 0x2067, 0x2066, 0x2068, 0x2069))
ALEF = chr(0x05D0)
SHALOM = "".join(chr(c) for c in (0x05E9, 0x05DC, 0x05D5, 0x05DD))
OLAM = "".join(chr(c) for c in (0x05E2, 0x05D5, 0x05DC, 0x05DD))
MEEM = chr(0x0645)
MARHABA = "".join(chr(c) for c in (0x0645, 0x0631, 0x062D, 0x0628, 0x0627))


def chars(*codes):
    """The string of these code points."""
    return "".join(chr(c) for c in codes)


def js_escapes(*codes):
    """JavaScript escape text for each code point, such as backslash u 202a, as plain ASCII."""
    return "".join(BS + "u%04x" % c for c in codes)


def js_range(low, high):
    return BS + "u%04x-" % low + BS + "u%04x" % high
