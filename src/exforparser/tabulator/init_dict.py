from exfor_dictionary.exfor_dict import Diction

d = Diction()
## get possible heading list
x_en_heads = d.get_incident_en_heads()
x_en_err_heads = d.get_incident_en_err_heads()
y_data_heads = d.get_data_heads()
y_data_err_heads = d.get_data_err_heads()
