# Touchstone documentation: https://ibis.org/touchstone_ver2.1/touchstone_ver2_1.pdf

def write_touchstone(touchstone_dict):
    keys_list = list(touchstone_dict.keys())
    if ('Z_ref' not in keys_list):
        print("ERROR NO Z_REF GIVEN")
    if ('S' not in keys_list):
        print("No s-params given")
    if ('MHz' not in keys_list):
        print("no frequency passed")
    
    file = open(f"{touchstone_dict['path_name']}.s1p", "w")

    # Option Line (S-param, RI (real-imaginary), )
    file.write(f"# MHz S RI R {touchstone_dict['Z_ref']}\n")
    
    for i in range(len(touchstone_dict['S'])):
        freq = touchstone_dict['MHz'][i]
        s_param = touchstone_dict['S'][i]
        file.write(f"{freq / 1e6} {s_param.real} {s_param.imag}\n")

    file.close()