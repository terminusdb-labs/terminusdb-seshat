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
    epistemic_state: Optional['EpistemicState']
    scope: Optional['ScopedValue']
    value: str
    number: Optional[int]


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
    mil_tech: 'MilitaryTechnologies'

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
#df_section = df_polity.get_group("AfDurrn").groupby("Section")
print(df_polity)
#find words with highest frequency in column to conver to booleans
#for name in list_polity_name:
#    df_section = df_polity.groupby("Section")
# df_test = df_section.get_group("Warfare variables").groupby("Subsection").get_group("Military Technologies")



# #print(df_test)
# value_str = df_test["Variable"].unique()
# #print(value_str)
# list_weapons = []

def epistemic_state_func(actual_value):
    if actual_value == "present":
        return EpistemicState.present
    elif actual_value == "absent":
        return EpistemicState.absent
    elif actual_value == "UNKNOWN":
        return EpistemicState.unknown

def scoped_value_func(actual_value):
    section = ScopedValue()
    if actual_value == "inferred":
        section.inferred = True
    elif actual_value == "suspected":
        section.suspected == True
    return section


user = "dani"
team = "PAOK-test"  # My team name.
endpoint = f"https://cloud.terminusdb.com/PAOK-test/"
client = WOQLClient(endpoint)

client.connect(user=user, team=team, use_token=True)

exists = client.get_database("seshat.v1")
if exists:
    client.delete_database("seshat.v1")
client.create_database("seshat.v1")  # reset the DB

seshat_schema.commit(client, commit_msg="Adding Schema")




for polity in df_polity:
    polity_military_tech = polity[1].loc[(polity[1]["Section"] == "Warfare variables") &
                      (polity[1]["Subsection"] == "Military Technologies")]
    technology = polity_military_tech["Variable"]
    list_weapons=[]
    for tech_variable in technology:
        ep_state = polity_military_tech.loc[polity_military_tech["Variable"]
                                            == tech_variable]
        ep_state_v = epistemic_state_func(
            ep_state["ActualValue"].iloc[0])
        section_v = scoped_value_func(ep_state["Confidence"].iloc[0])
        weapon_value = MilitaryTechValue(epistemic_state=ep_state_v, value=tech_variable,
        scope = section_v)
        list_weapons.append(weapon_value)

    milit_tech_list = MilitaryTechnologies()
    milit_tech_list.military_technologies = list_weapons
    pp.pprint(milit_tech_list._obj_to_dict())

    pol_doc = Polity(polid=polity[0], originalID=polity[0],
                     mil_tech=milit_tech_list)
    client.insert_document(pol_doc, commit_msg=f"Inserting data")








# for technology in value_str:
#     ep_state = df_test.loc[df_test["Variable"] == technology]
#     #print(type(ep_state["Variable"].iloc[0]))
#     ep_state_v = epistemic_state_func(ep_state["ActualValue"].iloc[0])
#     section_v = scoped_value_func(ep_state["Confidence"].iloc[0])
#     #print(ep_state["Confidence"].iloc[0])
#     # ep_state_v = EpistemicS
#     weapon_value = MilitaryTechValue(epistemic_state=ep_state_v, value=technology,
#     scope = section_v)
#     #pp.pprint(pew_pew_value._obj_to_dict)
#     list_weapons.append(weapon_value)

# milit_tech_list = MilitaryTechnologies()
# milit_tech_list.military_technologies = list_weapons
# pp.pprint(milit_tech_list._obj_to_dict())


# afdurn = Polity(polid='af_durn', originalID='Afdurrn',
#                 mil_tech=milit_tech_list)


# user = "dani"
# team = "PAOK-test"  # My team name.
# endpoint = f"https://cloud.terminusdb.com/PAOK-test/"
# client = WOQLClient(endpoint)

# client.connect(user=user, team=team, use_token=True)

# exists = client.get_database("seshat.v1")
# if exists:
#     client.delete_database("seshat.v1")
# client.create_database("seshat.v1")  # reset the DB

# seshat_schema.commit(client, commit_msg="Adding Schema")
# client.insert_document(afdurn, commit_msg=f"Inserting data")


