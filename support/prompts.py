from support import version

__author__ = version.get_author()
__version__ = version.get_version()

def base_int_input(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        print('Invalid Input. Integers only accepted, try again.')
        return base_int_input(prompt)
def input_range(prompt, min, max):
    raw_input = base_int_input(prompt)
    while raw_input < min or raw_input > max:
        print('Inavlid Input. Valid input range {}-{}, try again.'.format(min, max))
        raw_input = base_int_input(prompt)
    return raw_input

def project_selection(projects):
    projects_len = projects.__len__() + 1
    print('\nSelect project to import .ical to from list below:')
    for idx, project in enumerate(projects):
        print('    {}) {} - ID: {}'.format(idx+1, project[1], project[0]))
    print('    {}) New Project'.format(projects_len))
    return input_range('Selection: ', 1, projects_len)