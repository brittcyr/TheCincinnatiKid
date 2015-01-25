


def java_string_hashcode(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


#StringBuilder().append(Math.abs((String.valueOf(team) + round + RunMatches.SALT).hashCode())).toString();

# Day 6: TheCincinnatiKid   hashes to 19067956452

def break_their_hash_name(team="TheCincinnatiKid", rnd='6'):
    for rnd in xrange(100000000):
        salt = "randomstring"
        prehash = team + str(rnd) + salt
        seed = abs(java_string_hashcode(prehash))
        if seed ==  1906795645:
            print 'SOLVED the name anonymizer for me with rnd = ', rnd
            return


break_their_hash_name()

