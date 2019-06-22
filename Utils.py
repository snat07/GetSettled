import stringdist

def alias_dictionary(a1, a2, treshold = 0.6):
        aliases = {}
        for nei in a1:
            alias = String_conversion()
            alias.text = nei
            aliases[nei] = alias
            for bar in a2:
                distance = stringdist.levenshtein_norm(nei.lower(),bar.lower())
                if distance < alias.value and distance <= treshold:
                    alias.value = distance
                    alias.text = bar
                    aliases[nei] = alias                
        return aliases   

def alias_list(aliases):
    alias = []
    for key in aliases:
        if aliases[key].value < 1:
            alias.append(aliases[key].text)
    return alias

def real_list(aliases):
    real = []
    for key in aliases:
        if aliases[key].value < 1:
            real.append(key)
    return real

def alias_values(aliases):
    for key in aliases:
        if aliases[key].value >= 0:
            print(key + ' ---- ' + aliases[key].text + ' ----- ' + str(aliases[key].value))

class String_conversion:
    text = ''
    value = 1