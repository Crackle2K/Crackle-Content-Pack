"""Gen 1 base XP yields and growth rates (sourced from Bulbapedia/PokeAPI)."""


# growth_rate -> total XP needed to reach level n
def xp_for_level(n: int, growth_rate: str) -> int:
    if n <= 1:
        return 0
    if growth_rate == "fast":
        return 4 * n**3 // 5
    elif growth_rate == "medium-slow":
        return max(0, 6 * n**3 // 5 - 15 * n**2 + 100 * n - 140)
    elif growth_rate == "slow":
        return 5 * n**3 // 4
    else:  # medium-fast (default)
        return n**3


# (base_experience, growth_rate)
GEN1_XP = {
    1: (64, "medium-slow"), 2: (142, "medium-slow"), 3: (236, "medium-slow"),
    4: (62, "medium-slow"), 5: (142, "medium-slow"), 6: (240, "medium-slow"),
    7: (63, "medium-slow"), 8: (142, "medium-slow"), 9: (239, "medium-slow"),
    10: (39, "fast"), 11: (72, "fast"), 12: (178, "medium-fast"),
    13: (39, "fast"), 14: (72, "fast"), 15: (178, "medium-fast"),
    16: (50, "medium-slow"), 17: (122, "medium-slow"), 18: (216, "medium-slow"),
    19: (51, "medium-fast"), 20: (145, "medium-fast"),
    21: (52, "medium-fast"), 22: (155, "medium-fast"),
    23: (58, "medium-fast"), 24: (157, "medium-fast"),
    25: (112, "medium-fast"), 26: (218, "medium-fast"),
    27: (60, "medium-fast"), 28: (158, "medium-fast"),
    29: (55, "medium-slow"), 30: (128, "medium-slow"), 31: (227, "medium-slow"),
    32: (55, "medium-slow"), 33: (128, "medium-slow"), 34: (227, "medium-slow"),
    35: (113, "fast"), 36: (217, "fast"),
    37: (60, "medium-fast"), 38: (177, "medium-fast"),
    39: (95, "fast"), 40: (196, "fast"),
    41: (49, "medium-fast"), 42: (159, "medium-fast"),
    43: (64, "medium-slow"), 44: (138, "medium-slow"), 45: (221, "medium-slow"),
    46: (57, "medium-fast"), 47: (142, "medium-fast"),
    48: (61, "medium-fast"), 49: (158, "medium-fast"),
    50: (53, "medium-fast"), 51: (149, "medium-fast"),
    52: (58, "medium-fast"), 53: (154, "medium-fast"),
    54: (64, "medium-fast"), 55: (175, "medium-fast"),
    56: (61, "medium-fast"), 57: (159, "medium-fast"),
    58: (70, "slow"), 59: (194, "slow"),
    60: (60, "medium-slow"), 61: (135, "medium-slow"), 62: (230, "medium-slow"),
    63: (62, "medium-slow"), 64: (140, "medium-slow"), 65: (225, "medium-slow"),
    66: (61, "medium-slow"), 67: (142, "medium-slow"), 68: (227, "medium-slow"),
    69: (60, "medium-slow"), 70: (137, "medium-slow"), 71: (221, "medium-slow"),
    72: (67, "slow"), 73: (180, "slow"),
    74: (60, "medium-slow"), 75: (137, "medium-slow"), 76: (223, "medium-slow"),
    77: (82, "medium-fast"), 78: (175, "medium-fast"),
    79: (63, "medium-slow"), 80: (172, "medium-slow"),
    81: (65, "medium-fast"), 82: (163, "medium-fast"),
    83: (132, "medium-fast"),
    84: (62, "medium-fast"), 85: (165, "medium-fast"),
    86: (65, "medium-fast"), 87: (166, "medium-fast"),
    88: (65, "medium-fast"), 89: (175, "medium-fast"),
    90: (61, "slow"), 91: (184, "slow"),
    92: (62, "medium-slow"), 93: (142, "medium-slow"), 94: (225, "medium-slow"),
    95: (77, "medium-fast"),
    96: (66, "medium-fast"), 97: (169, "medium-fast"),
    98: (65, "medium-fast"), 99: (166, "medium-fast"),
    100: (66, "medium-fast"), 101: (168, "medium-fast"),
    102: (65, "slow"), 103: (182, "slow"),
    104: (64, "medium-fast"), 105: (149, "medium-fast"),
    106: (159, "medium-fast"), 107: (159, "medium-fast"),
    108: (127, "medium-fast"),
    109: (68, "medium-fast"), 110: (172, "medium-fast"),
    111: (69, "slow"), 112: (170, "slow"),
    113: (395, "fast"),
    114: (166, "medium-fast"),
    115: (172, "medium-fast"),
    116: (59, "medium-fast"), 117: (154, "medium-fast"),
    118: (64, "medium-fast"), 119: (158, "medium-fast"),
    120: (68, "slow"), 121: (182, "slow"),
    122: (161, "medium-fast"),
    123: (100, "medium-fast"),
    124: (159, "medium-fast"),
    125: (172, "medium-fast"),
    126: (173, "medium-fast"),
    127: (175, "medium-fast"),
    128: (172, "medium-fast"),
    129: (40, "slow"), 130: (189, "slow"),
    131: (187, "slow"),
    132: (101, "medium-fast"),
    133: (65, "medium-fast"), 134: (184, "medium-fast"),
    135: (184, "medium-fast"), 136: (184, "medium-fast"),
    137: (79, "medium-fast"),
    138: (71, "medium-fast"), 139: (173, "medium-fast"),
    140: (71, "medium-fast"), 141: (173, "medium-fast"),
    142: (180, "slow"),
    143: (189, "slow"),
    144: (261, "slow"), 145: (261, "slow"), 146: (261, "slow"),
    147: (60, "slow"), 148: (147, "slow"), 149: (270, "slow"),
    150: (306, "slow"),
    151: (270, "medium-slow"),
}
