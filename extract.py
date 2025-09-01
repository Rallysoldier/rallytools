def extract(
        outer: dict[str,dict[str,any]]=None,
        inner: any='',
        lookup: str='',
        listme: str='',
        intme: str='',
        strme: str='',
        tolower: str='',
        printme: str='',
        delim: str=", "
    ):
    ''' Flexible multitool for retrieving data from nested dicts '''
    if outer and inner and lookup:
        solution = outer[inner][lookup]
    elif outer and not inner and lookup:
        solution = []
        for key, value in outer.items():
            for subkey, subvalue in value.items():
                if subkey == lookup:
                    solution.append(f"{key}: {subkey}: {subvalue}")
    elif outer and inner and not lookup:
        solution = outer[inner]
    if listme and type(solution) == str:
        solution = solution.split(delim)
    if intme:
        try:
            if type(solution) == list:
                solution = list(map(int, solution))
            else:
                solution = int(solution)
        except ValueError:
            print("Error: Unable to convert to an integer. Invalid input.")
        except TypeError:
            print("Error: Type mismatch. Expected a value that can be converted to an integer.")
    if strme:
        try:
            solution = str(solution)
            if tolower:
                solution = solution.lower()
        except ValueError:
            print("Error: Unable to convert to a str. Invalid input.")
        except TypeError:
            print("Error: Type mismatch. Expected a value that can be converted to an integer.")
    if printme:
        print(solution)
    return solution