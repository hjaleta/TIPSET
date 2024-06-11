import textwrap

def rst_toctree(files, directives = None):

    if directives is None:
        directives = {}

    """
    Create a toctree for a .rst file
    """
    toctree = textwrap.dedent(
    f"""
    .. toctree::
    """
    )
    
    for directive, value in directives.items():
        toctree += f"    :{directive}: {value}\n"

    toctree += "\n"
    for file in files:
        toctree += f"    {file}\n"
    
    return toctree

def rst_csv_table(file_path, title=None, directives = None):
    """
    Create a csv table for a .rst file
    """

    directives_to_use = {
        "header-rows": 1,
    }

    if isinstance(directives, dict):
        directives_to_use.update(directives)
    
    csv_table = textwrap.dedent(
    f"""
    .. csv-table:: {title}
        :file: {file_path}
    """)
    
    for directive, value in directives_to_use.items():
        csv_table += f"    :{directive}: {value}\n"
    
    return csv_table