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


class Society(Topic):
    '''Social variables'''
    _schema = seshat_schema
    _abstract = []


class Military(Topic):
   '''Military variables'''
   _schema = seshat_schema
   _abstract = []


class General(Topic):
   '''General variables'''
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


class MilitaryTechValue(Military):
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


class RAValue(Military, Society, General):
    _schema = seshat_schema
    _subdocument = []
    _key = RandomKey
    r_a_value: str


class Ra(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    r_a_list: List['RAValue']


class InstitutionalVariables(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    r_a: 'Ra'


class WarfareVariables(DocumentTemplate):
   _schema = seshat_schema
   _subdocument = []
   military_technologies: 'MilitaryTechnologies'
   r_a: 'Ra'


class Status(Society):
    _schema = seshat_schema
    _subdocument = []
    _key = RandomKey
    epistemic_state: Optional['EpistemicState']
    scope: Optional['ScopedValue']
    value: Optional[str]


class SocialMobility(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    status: List['Status']


class AlternativeNamesValue(General):
    _schema = seshat_schema
    _subdocument = []
    alt_name: str


class AlternativeNames(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    alternative_names_list: List['AlternativeNamesValue']


class CapitalValue(General):
    _schema = seshat_schema
    _subdocument = []
    capital_val: str


class Capital(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    capital_list: List['CapitalValue']


class DegreeCentralizationValue(General):
    _schema = seshat_schema
    _subdocument = []
    degree_centr_val: str


class DegreeCentralization(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    degree_centr_list: List['DegreeCentralizationValue']


class LanguageValue(General):
    _schema = seshat_schema
    _subdocument = []
    language_val: str


class Language(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    language_list: List['LanguageValue']


class GeneralValues(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    alternative_names: Optional['AlternativeNames']
    capital: Optional['Capital']
    degree_of_centralization: Optional['DegreeCentralization']
    language: Optional['Language']


class Polity(DocumentTemplate):
    _schema = seshat_schema
    polid: str
    _key = LexicalKey(["polid"])
    originalID: str
    warfare_variables: 'WarfareVariables'
    social_mobility: 'SocialMobility'
    institutional_variables: 'InstitutionalVariables'
    general_values: 'GeneralValues'


df = pd.read_csv("seshat_test.csv", sep='|')

list_polity_name = df["PolityName"].unique()
list_section_name = df["Section"].unique()
list_subsection_name = df["Subsection"].unique()
list_Variable = df["Variable"].unique()
list_actual_value = df["ActualValue"].unique()

df_polity = df.groupby("PolityName")


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
    # warfare variables -military technology
    polity_military_tech = polity[1].loc[(polity[1]["Section"] == "Warfare variables") &
                                         (polity[1]["Subsection"] == "Military Technologies")]
    technology = polity_military_tech["Variable"]
    list_weapons = []
    for tech_variable in technology:
        ep_state = polity_military_tech.loc[polity_military_tech["Variable"]
                                            == tech_variable]
        ep_state_v = epistemic_state_func(
            ep_state["ActualValue"].iloc[0])
        section_v = scoped_value_func(ep_state["Confidence"].iloc[0])
        if ep_state["ActualValue"].iloc[0].isdigit() == True:
            no_of_units = int(ep_state["ActualValue"].iloc[0])
            weapon_value = MilitaryTechValue(epistemic_state=ep_state_v, value=tech_variable,
                                             scope=section_v, number=no_of_units)
        else:
            weapon_value = MilitaryTechValue(epistemic_state=ep_state_v, value=tech_variable,
                                             scope=section_v)
        list_weapons.append(weapon_value)

    #warfare variables - RA
    polity_military_ra = polity[1].loc[(polity[1]["Section"] == "Warfare variables") &
                                       (polity[1]["Variable"] == "RA")]
    r_a_name = polity_military_ra["ActualValue"]
    list_ra = []
    for value in r_a_name:
        r_a_val = RAValue(r_a_value=value)
        list_ra.append(r_a_val)

    ### social mobility
    polity_social_mobility = polity[1].loc[(polity[1]["Section"] == "Social Mobility") &
                                           (polity[1]["Subsection"] == "Status")]
    status_list = polity_social_mobility["Variable"]
    list_status_polity = []
    for status_value in status_list:
        ep_state = polity_social_mobility.loc[polity_social_mobility["Variable"]
                                              == status_value]
        value = status_value
        ep_state_v = epistemic_state_func(
            ep_state["ActualValue"].iloc[0])
        section_v = scoped_value_func(ep_state["Confidence"].iloc[0])
        status_polity = Status(epistemic_state=ep_state_v, value=status_value,
                               scope=section_v)
        list_status_polity.append(status_polity)

    ## institutional variables
    polity_institutional_variables = polity[1].loc[polity[1]
                                                   ["Section"] == "Institutional Variables"]
    r_a_name = polity_institutional_variables["ActualValue"]
    list_ra_i_v = []
    for value in r_a_name:
        r_a_val = RAValue(r_a_value=value)
        list_ra_i_v.append(r_a_val)

    ## general variables
    polity_gen_var = polity[1].loc[polity[1]["Section"] == "General variables"]
    ## general variables - alt names
    gen_var_alt_name = polity_gen_var.loc[polity_gen_var["Variable"]
                                          == "Alternative names"]["ActualValue"]
    list_gen_var_alt_names = []
    for name in gen_var_alt_name:
        name_val = AlternativeNamesValue(alt_name=name)
        list_gen_var_alt_names.append(name_val)
    ## general variables - capital
    gen_var_capital = polity_gen_var.loc[polity_gen_var["Variable"]
                                         == "Capital"]["ActualValue"]
    list_gen_var_capital = []
    for cap in gen_var_capital:
        cap_val = CapitalValue(capital_val=cap)
        list_gen_var_capital.append(cap_val)
    ## general variables - degree of centralization
    gen_var_deg_centr = polity_gen_var.loc[polity_gen_var["Variable"]
                                           == "Degree of centralization"]["ActualValue"]
    list_gen_var_deg_centr = []
    for deg in gen_var_deg_centr:
        deg_val = DegreeCentralizationValue(degree_centr_val=deg)
        list_gen_var_deg_centr.append(deg_val)
    ## general variables - language
    gen_var_lang = polity_gen_var.loc[polity_gen_var["Variable"]
                                      == "Language"]["ActualValue"]
    list_gen_var_lang = []
    for lang in gen_var_lang:
        lang_val = LanguageValue(language_val=lang)
        list_gen_var_lang.append(lang_val)

    lang_list = Language(language_list=list_gen_var_lang)
    capital_list = Capital(capital_list=list_gen_var_capital)
    degree_centralization_list = DegreeCentralization(
        degree_centr_list=list_gen_var_deg_centr)
    alt_names = AlternativeNames(alternative_names_list=list_gen_var_alt_names)
    general_val = GeneralValues()
    general_val.alternative_names = alt_names
    general_val.capital = capital_list
    general_val.degree_of_centralization = degree_centralization_list
    general_val.language = lang_list
    inst_var_author_list = Ra()
    inst_var_author_list.r_a_list = list_ra_i_v
    inst_var = InstitutionalVariables()
    inst_var.r_a = inst_var_author_list

    soc_mob = SocialMobility()
    soc_mob.status = list_status_polity
    author_list = Ra()
    author_list.r_a_list = list_ra
    milit_tech_list = MilitaryTechnologies()
    milit_tech_list.military_technologies = list_weapons
    warf_var = WarfareVariables()
    warf_var.military_technologies = milit_tech_list
    warf_var.r_a = author_list
    #pp.pprint(milit_tech_list._obj_to_dict())

    pol_doc = Polity(polid=polity[0], originalID=polity[0],
                     warfare_variables=warf_var, social_mobility=soc_mob, institutional_variables=inst_var,
                     general_values=general_val)
    client.insert_document(pol_doc, commit_msg=f"Inserting data")
