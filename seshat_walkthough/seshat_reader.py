import pandas as pd

from terminusdb_client.woqlschema import WOQLSchema, DocumentTemplate, LexicalKey, EnumTemplate, HashKey, RandomKey
from terminusdb_client import WOQLClient
from typing import List, Optional, Set
from enum import Enum
import pprint as pp

seshat_schema = WOQLSchema()


class Topic(DocumentTemplate):
    '''Root of topic hierarchy'''
    _schema = seshat_schema
    _abstract = []


class EpistemicState(EnumTemplate):
    '''Enumeration Type'''
    _schema = seshat_schema
    absent = ()
    absent_to_present = ()
    present = ()
    present_to_absent = ()
    unknown = ()


class WarfareVariables(Topic):
   '''Miltiary variables'''
   _schema = seshat_schema
   _abstract = []


class ScopedValue(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    #dates: Optional['GYearRange']
    unknown: Optional[bool]
    suspected: Optional[bool]
    disputed: Optional[bool]
    inferred: Optional[bool]


class MilitaryTechValue(WarfareVariables):
    _schema = seshat_schema
    _subdocument = []
    _key = RandomKey
    epistemic_state: 'EpistemicState'
    scope: 'ScopedValue'
    value: str
    number: int


class MilitaryTechnologies(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    military_technologies: List['MilitaryTechValue']


class Polity(DocumentTemplate):
    _schema = seshat_schema
    #_key = LexicalKey("polid")
    polid: str  # the equivalent of 'label'?  JSB? Note use of str, not 'xsd:string'?
    _key = LexicalKey(["polid"])
    originalID: str  # to compare with the old wiki polity page names
    # in order to permit uncertain or disputed values with different dates all seshat properties are Set[]
    mil_tech: 'MilitaryTechnologies'  # typically only one but could be disputed


### Scope ofthis is to get a basic json schema and doc export from a seshat csv file.
df = pd.read_csv("seshat_test.csv", sep='|')


#df["ActualValue"] = df["ActualValue"].apply(
#    lambda x: x.replace("present", EpistemicState.present))

#convert this to a for in list columns group
list_polity_name = df["PolityName"].unique()
list_section_name = df["Section"].unique()
list_subsection_name = df["Subsection"].unique()
list_Variable = df["Variable"].unique()
list_actual_value = df["ActualValue"].unique()

df_polity = df.groupby("PolityName")
df_section = df_polity.get_group("AfDurrn").groupby("Section")
#find words with highest frequency in column to conver to booleans
#for name in list_polity_name:
#    df_section = df_polity.groupby("Section")
df_test = df_section.get_group("Warfare variables").groupby("Subsection").get_group("Military Technologies")
j = (df_test.groupby(['Subsection'])
       .apply(lambda x: dict(zip(x.Variable, x.ActualValue)))
       .reset_index()
       .rename(columns={0: "Value"})
       .to_json(orient='records'))

#print(df_test)
value_str = df_test["Variable"].unique()
#print(value_str)
list_weapons = []


def epistemic_state_func(actual_value):
    if actual_value == "present":
        return EpistemicState.present
    elif actual_value == "absent":
        return EpistemicState.absent
    elif actual_value == "UNKNOWN":
        return EpistemicState.unknown
    else:
        return int(actual_value)

def scoped_value_func(actual_value):
    section = ScopedValue()
    if actual_value == "inferred":
        section.inferred = True
    elif actual_value == "suspected":
        section.suspected == True

for technology in value_str:
    ep_state = df_test.loc[df_test["Variable"] == technology]
    #print(list)
    ep_state_v = ep_state["ActualValue"].apply(epistemic_state_func)
    section_v = ep_state["Confidence"].apply(scoped_value_func)
    pew_pew_value = MilitaryTechValue(epistemic_state=ep_state_v, value=technology,
    scope = section_v)
    list_weapons.append(pew_pew_value)

milit_tech_list = MilitaryTechnologies()
milit_tech_list.military_technologies = list_weapons


afdurn = Polity(polid='af_durn', originalID='Afdurrn',
                mil_tech=milit_tech_list)


user = "dani"
team = "PAOK-test"  # My team name.
endpoint = f"https://cloud.terminusdb.com/PAOK-test/"
client = WOQLClient(endpoint)

client.connect(user=user, team=team, use_token=True)

exists = client.get_database("seshat.v1")
if exists:
    client.delete_database("seshat.v1")
client.create_database("seshat.v1")  # reset the DB

#commit schema?
client.insert_document(afdurn, commit_msg=f"Inserting data")


