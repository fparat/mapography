# coding: utf-8


def list(maptext, parser):
    return '\n\n'.join(str(m) for m in parser.get_modules(maptext))


def sizes(maptext, parser):
    modules = parser.get_modules(maptext)

    # Find section names
    secnames = set(seg.name for m in modules for seg in m.segments)

    # Find and regroup the modules by section type, sorted
    sizes = []
    for secname in secnames:
        section = {'name': secname, 'modules': []}
        for m in modules:
            for seg in m.segments:
                if seg.name == secname:
                    section['modules'].append((m.name, len(seg)))
                    break
        section['modules'].sort(key=lambda m: m[1], reverse=True)
        sizes.append(section)
    # the complicated lambda is for putting names starting with '.' at the end
    sizes.sort(key=lambda s: ['1', '0'][s['name'][0].isalpha()] + s['name'])

    # Formatting
    results = []
    for section in sizes:
        module_list = '\n'.join(['{} ({})'.format(*m)
                                 for m in section['modules']])
        bloc = '{}:\n{}'.format(section['name'], module_list)
        results.append(bloc)

    return '\n\n'.join(results)


