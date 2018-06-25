from django.shortcuts import render
import requests
import json
# Create your views here.
def index(request):
	#Get all the medication data from the api and convert it to usable JSON format
	medication_response = requests.get('http://api-sandbox.pillpack.com/medications')
	medications = medication_response.json()

	same_rxcui_dict = {}
	#Group branded and generic medications that have same rxcui so that one can be replaced with the other
	for drugs in medications:
		if drugs['rxcui'] not in same_rxcui_dict:
			same_rxcui_dict[drugs['rxcui']]={'generic':[], 'branded':[]}
		if drugs['generic']:
			same_rxcui_dict[drugs['rxcui']]['generic'].append(drugs['id'])
		else:
			same_rxcui_dict[drugs['rxcui']]['branded'].append(drugs['id'])

	replace_dict={}
	#For every branded medication, find a substitute generic medication and create a pair 
	for key, value in same_rxcui_dict.items():
		if any(same_rxcui_dict[key]['generic']) and any(same_rxcui_dict[key]['branded']):
			replace_dict[same_rxcui_dict[key]['branded'][0]] = same_rxcui_dict[key]['generic'][0]

	same_rxcui_dict.clear()
	#Get all the prescriptions from the api and convert it to the usable JSON format
	prescription_response = requests.get('http://api-sandbox.pillpack.com/prescriptions')
	prescriptions = prescription_response.json()

	#For each prescription check if substitute/update is available and if available add it to updates
	prescription_update = []
	for prescription in prescriptions:
		if prescription['medication_id'] in replace_dict:
			prescription_update.append({'medication_id':replace_dict[prescription['medication_id']], 'prescription_id':prescription['id']})

	replace_dict.clear()

	#Create a JSON file for the all the updates 
	with open("prescription_updates.json", 'w') as JSONfile:
		json.dump(prescription_update, JSONfile, indent=4)
	
	# Add all the medications that are branded to a dictionary
	branded_medications = {}
	for medication in medications:
		if not medication['generic']:
			branded_medications[medication['id']]=medication
	
	#
	prescriptions_needing_sub = []
	#Add all the prescriptions that need substitutions to a list
	for prescription in prescriptions:
		if prescription['medication_id'] in branded_medications:
			needs_sub={
				'prescription_id': prescription['id'],
				'medication_id': prescription['medication_id'],
				'description': branded_medications[prescription['medication_id']]['description']
			}
			prescriptions_needing_sub.append(needs_sub)

	#Create a context that holds the data that we want to render to our app
	contexts = {'prescriptions_needing_sub': prescriptions_needing_sub, 'prescription_update':prescription_update}

	return render(request, 'Pillpack_Prescriptions/index.html', contexts)